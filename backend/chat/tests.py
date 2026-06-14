from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from chat.models import Conversation, Message, MessageRole
from chat.services.chat_service import ChatService
from chat.services.prompt_service import PromptService, prompt_service
from chat.services.llm_service import LLMService, ProxyLLM
from chat.services.langfuse_logger import LangfuseLogger


def make_user(username='alice'):
    return User.objects.create_user(username=username, password='password123', email=f'{username}@x.com',
                                    first_name='Al', last_name='Ice')


# --- Models ------------------------------------------------------------------

class ChatModelTests(APITestCase):
    def test_conversation_and_message_str(self):
        user = make_user()
        conv = Conversation.objects.create(user=user)
        self.assertIn(user.username, str(conv))
        msg = Message.objects.create(conversation=conv, role=MessageRole.USER, content='hello there')
        self.assertIn('user', str(msg))


# --- PromptService -----------------------------------------------------------

class PromptServiceTests(APITestCase):
    def setUp(self):
        self.user = make_user()

    def test_build_user_context_no_resume(self):
        ctx = prompt_service.build_user_context(self.user)
        self.assertIn('User Profile:', ctx)
        self.assertIn('Not yet generated', ctx)

    def test_build_user_context_with_full_resume(self):
        from resumes.models import Resume, NextBestStep, CareerPathway, CareerStage, SkillCourseRecommendation
        resume = Resume.objects.create(
            user=self.user, is_active=True, target_designation='Senior Dev',
            total_exp=5, it_skills=['Python', 'Django'],
        )
        step = NextBestStep.objects.create(
            resume=resume, title='Learn Kubernetes', impact='High',
            recommended_skills=['Docker', 'K8s'],
        )
        SkillCourseRecommendation.objects.create(
            next_step=step, skill='Learn Kubernetes',
            courses=[{'title': 'K8s 101', 'platform': 'Coursera', 'instructor': 'Bob', 'link': 'http://x'},
                     'not-a-dict'],
        )
        pathway = CareerPathway.objects.create(
            resume=resume, current_level='Junior', target_role='Senior',
            timeline_total='2 years',
        )
        CareerStage.objects.create(
            pathway=pathway, title='Stage 1', duration='6 months', status='current',
            skills=['Python'], milestones=['Ship feature'], order=0,
        )
        ctx = prompt_service.build_user_context(self.user)
        self.assertIn('Senior Dev', ctx)
        self.assertIn('Learn Kubernetes', ctx)
        self.assertIn('K8s 101', ctx)
        self.assertIn('Junior → Senior', ctx)
        self.assertIn('Stage 1', ctx)

    def test_build_user_context_string_skills(self):
        from resumes.models import Resume
        Resume.objects.create(user=self.user, is_active=True, it_skills='Python and SQL')
        ctx = prompt_service.build_user_context(self.user)
        self.assertIn('Python and SQL', ctx)

    def test_build_user_context_handles_exception(self):
        broken = SimpleNamespace(first_name='X', last_name='Y')
        # Accessing .resumes raises AttributeError -> fallback path.
        ctx = prompt_service.build_user_context(broken)
        self.assertIn('Career guidance seeker', ctx)

    def test_build_system_prompt(self):
        out = PromptService.build_system_prompt('CTX', 'CONV')
        self.assertIn('CTX', out)
        self.assertIn('CONV', out)

    def test_build_nudge_system_prompt(self):
        out = PromptService.build_nudge_system_prompt('CTX')
        self.assertIn('CTX', out)

    def test_build_conversation_context_empty(self):
        self.assertEqual(PromptService.build_conversation_context([]), '')

    def test_build_conversation_context_truncates_long(self):
        msgs = [{'role': 'user', 'content': 'x' * 300}]
        out = PromptService.build_conversation_context(msgs)
        self.assertIn('...', out)
        self.assertIn('User:', out)


# --- ChatService -------------------------------------------------------------

class ChatServiceTests(APITestCase):
    def setUp(self):
        self.user = make_user()

    def test_get_or_create_conversation_creates_new(self):
        conv = ChatService.get_or_create_conversation(user=self.user)
        self.assertIsNotNone(conv.id)

    def test_get_or_create_conversation_returns_existing(self):
        conv = Conversation.objects.create(user=self.user)
        same = ChatService.get_or_create_conversation(conversation_id=str(conv.id), user=self.user)
        self.assertEqual(conv.id, same.id)

    def test_get_or_create_conversation_unknown_id_creates_new(self):
        import uuid
        conv = ChatService.get_or_create_conversation(conversation_id=str(uuid.uuid4()), user=self.user)
        self.assertIsNotNone(conv.id)

    def test_get_conversation_messages_orders_chronologically(self):
        conv = Conversation.objects.create(user=self.user)
        ChatService.add_message(conv, 'user', 'first')
        ChatService.add_message(conv, 'assistant', 'second')
        msgs = ChatService.get_conversation_messages(conv)
        self.assertEqual([m['content'] for m in msgs], ['first', 'second'])

    def test_add_message_roles(self):
        conv = Conversation.objects.create(user=self.user)
        self.assertEqual(ChatService.add_message(conv, 'user', 'a').role, MessageRole.USER)
        self.assertEqual(ChatService.add_message(conv, 'assistant', 'b').role, MessageRole.ASSISTANT)
        self.assertEqual(ChatService.add_message(conv, 'system', 'c').role, MessageRole.SYSTEM)

    def test_add_message_invalid_role(self):
        conv = Conversation.objects.create(user=self.user)
        with self.assertRaises(ValueError):
            ChatService.add_message(conv, 'robot', 'x')

    def test_build_user_context_delegates(self):
        self.assertIn('User Profile', ChatService.build_user_context(self.user))

    @patch('chat.services.chat_service.llm_service')
    def test_process_chat_message_success(self, mock_llm):
        mock_llm.generate_response.return_value = 'AI reply'
        mock_llm.model_name = 'test-model'
        reply, conv_id = ChatService.process_chat_message('Hi', self.user)
        self.assertEqual(reply, 'AI reply')
        self.assertEqual(Message.objects.filter(conversation_id=conv_id).count(), 2)

    @patch('chat.services.chat_service.llm_service')
    def test_process_chat_message_error_saves_fallback(self, mock_llm):
        conv = Conversation.objects.create(user=self.user)
        mock_llm.generate_response.side_effect = RuntimeError('boom')
        mock_llm.model_name = 'test-model'
        reply, conv_id = ChatService.process_chat_message('Hi', self.user, conversation_id=str(conv.id))
        self.assertIn('encountered an issue', reply)
        self.assertEqual(str(conv.id), conv_id)

    @patch('chat.services.chat_service.ChatService.build_user_context', side_effect=RuntimeError('boom'))
    def test_process_chat_message_error_without_conversation(self, _ctx):
        reply, conv_id = ChatService.process_chat_message('Hi', self.user)
        self.assertIn('encountered an issue', reply)
        self.assertIsNotNone(conv_id)


# --- ProxyLLM / LLMService ---------------------------------------------------

class ProxyLLMTests(APITestCase):
    def test_invoke_builds_payload_and_returns_content(self):
        proxy = ProxyLLM('http://proxy.local')
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
        messages = [
            SystemMessage(content='sys'),
            HumanMessage(content='hi'),
            AIMessage(content='prev'),
            'no-content-attr',
        ]
        with patch('chat.services.llm_service.requests.post') as mock_post:
            mock_post.return_value = MagicMock(
                raise_for_status=MagicMock(), json=MagicMock(return_value={'text': 'proxied'})
            )
            result = proxy.invoke(messages)
        self.assertEqual(result.content, 'proxied')
        payload = mock_post.call_args.kwargs['json']
        self.assertIn('systemInstruction', payload)
        self.assertEqual(len(payload['contents']), 2)

    def test_invoke_raises_on_error(self):
        proxy = ProxyLLM('http://proxy.local')
        with patch('chat.services.llm_service.requests.post', side_effect=RuntimeError('down')):
            with self.assertRaises(Exception):
                proxy.invoke([])


class LLMServiceTests(APITestCase):
    def test_production_with_proxy_url(self):
        def fake_getenv(k, d=None):
            return {'ENVIRONMENT': 'production', 'LLM_PROXY_URL': 'http://p'}.get(k, d)
        with patch('os.getenv', side_effect=fake_getenv):
            svc = LLMService()
        self.assertIsInstance(svc.model, ProxyLLM)
        self.assertEqual(svc.model_name, 'gemini-3.1-flash-lite')

    def test_production_without_proxy_url(self):
        def fake_getenv(k, d=None):
            return 'production' if k == 'ENVIRONMENT' else None
        with patch('os.getenv', side_effect=fake_getenv):
            svc = LLMService()
        self.assertIsNone(svc.model)

    def test_development_without_key(self):
        def fake_getenv(k, d=None):
            return {'ENVIRONMENT': 'development'}.get(k, None)
        with patch('os.getenv', side_effect=fake_getenv):
            svc = LLMService()
        self.assertIsNone(svc.model)

    def test_development_with_key(self):
        def fake_getenv(k, d=None):
            return {'ENVIRONMENT': 'development', 'GOOGLE_API_KEY': 'key'}.get(k, d)
        with patch('os.getenv', side_effect=fake_getenv):
            with patch('chat.services.llm_service.ChatGoogleGenerativeAI') as mock_model:
                svc = LLMService()
        self.assertEqual(svc.model_name, 'gemini-3.1-flash-lite')
        mock_model.assert_called_once()

    def test_generate_response_no_model(self):
        svc = LLMService.__new__(LLMService)
        svc.model = None
        svc.model_name = None
        self.assertIn('unavailable', svc.generate_response('sys', [], 'hi'))

    def test_generate_response_success_with_history(self):
        svc = LLMService.__new__(LLMService)
        svc.model = MagicMock()
        svc.model.invoke.return_value = SimpleNamespace(content='answer')
        out = svc.generate_response('sys', [{'role': 'user', 'content': 'a'},
                                            {'role': 'assistant', 'content': 'b'}], 'hi')
        self.assertEqual(out, 'answer')

    def test_generate_response_list_content(self):
        svc = LLMService.__new__(LLMService)
        svc.model = MagicMock()
        svc.model.invoke.return_value = SimpleNamespace(content=[{'text': 'listed'}])
        self.assertEqual(svc.generate_response('sys', [], 'hi'), 'listed')

    def test_generate_response_error(self):
        svc = LLMService.__new__(LLMService)
        svc.model = MagicMock()
        svc.model.invoke.side_effect = RuntimeError('boom')
        self.assertIn('encountered an error', svc.generate_response('sys', [], 'hi'))


# --- LangfuseLogger ----------------------------------------------------------

class LangfuseLoggerTests(APITestCase):
    def test_no_key_disables_client(self):
        def fake_getenv(k, d=None):
            return d
        with patch('os.getenv', side_effect=fake_getenv):
            logger = LangfuseLogger()
        self.assertIsNone(logger.langfuse)
        self.assertIsNone(logger.create_trace('c', 1, {}))
        # log_llm_call / flush are no-ops without a client.
        logger.log_llm_call(None, 'm', 's', 'u', 'a', {})
        logger.flush()

    def test_create_trace_success(self):
        logger = LangfuseLogger.__new__(LangfuseLogger)
        logger.langfuse = MagicMock()
        trace = MagicMock(trace_id='trace-123')
        logger.langfuse.start_observation.return_value = trace
        self.assertEqual(logger.create_trace('c', 1, {}), 'trace-123')
        trace.end.assert_called_once()

    def test_create_trace_handles_error(self):
        logger = LangfuseLogger.__new__(LangfuseLogger)
        logger.langfuse = MagicMock()
        logger.langfuse.start_observation.side_effect = RuntimeError('boom')
        self.assertIsNone(logger.create_trace('c', 1, {}))

    def test_log_llm_call_sync_success_and_error(self):
        logger = LangfuseLogger.__new__(LangfuseLogger)
        logger.langfuse = MagicMock()
        logger.langfuse.start_observation.return_value = MagicMock()
        logger._log_llm_call_sync('t', 'model', 'sys', 'usr', 'resp',
                                  {'input_tokens': 1, 'output_tokens': 2, 'total_tokens': 3})
        logger.langfuse.start_observation.side_effect = RuntimeError('boom')
        # Swallows the error internally.
        logger._log_llm_call_sync('t', 'model', 'sys', 'usr', 'resp', {})

    def test_log_llm_call_submits_async(self):
        logger = LangfuseLogger.__new__(LangfuseLogger)
        logger.langfuse = MagicMock()
        logger.executor = MagicMock()
        logger.log_llm_call('trace', 'm', 's', 'u', 'a', {})
        logger.executor.submit.assert_called_once()

    def test_flush_sync_success_and_error(self):
        logger = LangfuseLogger.__new__(LangfuseLogger)
        logger.langfuse = MagicMock()
        logger._flush_sync()
        logger.langfuse.flush.side_effect = RuntimeError('boom')
        logger._flush_sync()


# --- ChatView ----------------------------------------------------------------

class ChatViewTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    def test_get_no_conversations(self):
        resp = self.client.get('/api/chat/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.data['conversation_id'])
        self.assertEqual(resp.data['messages'], [])

    def test_get_latest_conversation(self):
        conv = Conversation.objects.create(user=self.user)
        ChatService.add_message(conv, 'user', 'hi')
        resp = self.client.get('/api/chat/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['conversation_id'], str(conv.id))

    def test_get_specific_conversation(self):
        conv = Conversation.objects.create(user=self.user)
        resp = self.client.get(f'/api/chat/?conversation_id={conv.id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['conversation_id'], str(conv.id))

    def test_post_message_required(self):
        self.assertEqual(self.client.post('/api/chat/', {}).status_code, 400)

    def test_post_message_must_be_string(self):
        resp = self.client.post('/api/chat/', {'message': 123}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_post_invalid_conversation_id(self):
        resp = self.client.post('/api/chat/', {'message': 'hi', 'conversation_id': 'not-a-uuid'}, format='json')
        self.assertEqual(resp.status_code, 400)

    @patch('chat.views.ChatService.process_chat_message', return_value=('reply', 'cid'))
    def test_post_success(self, _mock):
        resp = self.client.post('/api/chat/', {'message': 'hello'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['response'], 'reply')

    @patch('chat.views.ChatService.process_chat_message', side_effect=RuntimeError('boom'))
    def test_post_internal_error(self, _mock):
        resp = self.client.post('/api/chat/', {'message': 'hello'}, format='json')
        self.assertEqual(resp.status_code, 500)

    @patch('chat.views.ChatService.get_conversation_messages', side_effect=RuntimeError('boom'))
    def test_get_internal_error(self, _mock):
        Conversation.objects.create(user=self.user)
        resp = self.client.get('/api/chat/')
        self.assertEqual(resp.status_code, 500)
