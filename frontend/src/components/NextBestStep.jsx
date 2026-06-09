import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { resumeAPI } from '../config/api-resume-processor';
import { resumeAPI as backendResumeAPI } from '../config/api-backend';
import { setPresenting, setIdle } from '../store/avatarSlice';
import CourseRecommendations from './CourseRecommendations';
import { formatSkill } from '../utils/skills';

// Compare skill names loosely (case / underscores / spacing) so we can tell
// whether a recommended skill is one the user already has.
const normalizeSkill = (skill) =>
  String(skill ?? '')
    .toLowerCase()
    .replace(/_/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

// The set of skills the user already has, normalized for loose comparison.
const ownedSkillSet = (resumeData) =>
  new Set(
    [...(resumeData?.it_skills || []), ...(resumeData?.soft_skills || [])].map(normalizeSkill)
  );

const NextBestStep = ({ resumeData, targetDesignation }) => {
  const dispatch = useDispatch();
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [courses, setCourses] = useState([]);
  const [loadingCourses, setLoadingCourses] = useState(false);

  // Clear recommendations when target designation changes
  useEffect(() => {
    setRecommendations(null);
    setCourses([]);
  }, [targetDesignation]);

  // Load existing recommendations when component mounts
  useEffect(() => {
    const loadExistingRecommendations = async () => {
      try {
        const response = await backendResumeAPI.getNextBestStep();
        const nextStep = response.data;
        
        // Show the saved recommendation as-is. It was filtered against the
        // user's skills when it was generated, and it should stay put until
        // the user explicitly regenerates — adding a skill must not change it.
        setRecommendations({
          title: nextStep.title,
          type: nextStep.skill_type,
          confidence: nextStep.confidence,
          skills: nextStep.recommended_skills,
          impact: nextStep.impact,
        });
        
        // Load course recommendations
        loadCourseRecommendations();
      } catch (error) {
        // No existing recommendations found, which is fine
        if (error.response?.status !== 404) {
          console.error('Failed to load existing recommendations:', error);
        }
      }
    };

    if (resumeData && targetDesignation) {
      loadExistingRecommendations();
    }
  }, [resumeData, targetDesignation]);

  // Load course recommendations
  const loadCourseRecommendations = async () => {
    setLoadingCourses(true);
    try {
      const response = await backendResumeAPI.getCourseRecommendations();
      setCourses(response.data.courses || []);
    } catch (error) {
      if (error.response?.status !== 404) {
        console.error('Failed to load course recommendations:', error);
      }
      setCourses([]);
    } finally {
      setLoadingCourses(false);
    }
  };

  const generateRecommendations = async () => {
    setLoading(true);
    dispatch(setPresenting('Fawkes is generating skill recommendations...'));
    try {
      const response = await resumeAPI.predictNextSingleSkill({
        itSkills: resumeData.it_skills,
        softSkills: resumeData.soft_skills,
        designation: targetDesignation,
      });
      
      const bestSkill = response.data.best_next_skill;
      const topSkills = response.data.top_3_skills;

      // The backend can still return skills the user already has (it normalizes
      // skill names differently than they're stored). So walk the ranked
      // candidate list — now up to 10 — and use the highest-ranked skill the
      // user doesn't already have. Falls back to the top skill if all are owned.
      const ownedSkills = ownedSkillSet(resumeData);
      const nextSkill =
        (topSkills || [])
          .filter((candidate) => candidate && candidate.skill)
          .find((candidate) => !ownedSkills.has(normalizeSkill(candidate.skill))) || bestSkill;
      
      if (bestSkill) {
        const recommendationData = {
          title: nextSkill.skill,
          type: nextSkill.type,
          confidence: nextSkill.confidence,
          skills: topSkills.map(skill => skill.skill),
          impact: nextSkill.confidence > 0.7 ? 'High' : nextSkill.confidence > 0.4 ? 'Medium' : 'Low',
        };
        
        setRecommendations(recommendationData);
        
        // Save to database
        try {
          await backendResumeAPI.saveNextBestStep({
            title: nextSkill.skill,
            skill_type: nextSkill.type,
            confidence: nextSkill.confidence,
            recommended_skills: topSkills.map(skill => skill.skill),
            impact: recommendationData.impact,
            target_designation: targetDesignation,
          });
        } catch (error) {
          console.error('Failed to save next step to database:', error);
        }
        
        dispatch(setPresenting('Fawkes has your skill recommendations ready!'));
        setTimeout(() => dispatch(setIdle()), 2000);
        
        // Load course recommendations after successful generation
        loadCourseRecommendations();
      } else {
        const fallbackData = {
          title: 'No recommendations available',
          skills: [],
          impact: 'Low',
        };
        
        setRecommendations(fallbackData);
        
        // Save fallback to database
        try {
          await backendResumeAPI.saveNextBestStep({
            title: 'No recommendations available',
            recommended_skills: [],
            impact: 'Low',
            target_designation: targetDesignation,
          });
        } catch (error) {
          console.error('Failed to save fallback next step to database:', error);
        }
        
        dispatch(setIdle());
      }
    } catch (error) {
      console.error('Failed to generate recommendations:', error);
      dispatch(setIdle());
    } finally {
      setLoading(false);
    }
  };

  // Display label for the skill type ("it" → "IT", otherwise capitalized)
  const typeLabel = recommendations?.type
    ? (recommendations.type.toLowerCase() === 'it' ? 'IT' : formatSkill(recommendations.type))
    : '';

  return (
    <div className="card p-5">
      <div className="mb-5">
        <h3 className="text-lg font-semibold text-gray-900">Next Best Step</h3>
        <p className="text-xs text-gray-400 mt-0.5">Skill recommendations</p>
      </div>

      {!recommendations ? (
        <div className="text-center py-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-emerald-50 mb-4">
            <svg className="w-6 h-6 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <p className="text-sm text-gray-500 mb-5 max-w-xs mx-auto">
            Get personalized recommendations based on your profile and target role
          </p>
          <button onClick={generateRecommendations} disabled={loading} className="btn-primary">
            {loading ? (
              <span className="inline-flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                Analyzing...
              </span>
            ) : 'Generate Recommendations'}
          </button>
        </div>
      ) : (
        <div className="space-y-4 animate-fade-in-up">
          {/* Spotlight: the single next best skill */}
          <div className="rounded-2xl bg-emerald-50 border border-emerald-100 px-5 py-6 text-center">
            <div className="inline-flex items-center justify-center w-11 h-11 rounded-2xl bg-emerald-100 mb-3">
              <svg className="w-6 h-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <p className="text-xs font-medium uppercase tracking-wider text-emerald-600">Your next skill to learn</p>
            <h4 className="mt-1.5 text-2xl font-bold text-gray-900 leading-tight break-words">{formatSkill(recommendations.title)}</h4>
            {typeLabel && (
              <p className="mt-1 text-sm text-gray-500">{typeLabel} skill</p>
            )}
            {recommendations.impact === 'High' && (
              <div className="mt-4 flex justify-center">
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-100 text-emerald-700">
                  <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 17l6-6 4 4 8-8m0 0h-5m5 0v5" />
                  </svg>
                  High Impact
                </span>
              </div>
            )}
          </div>

          <CourseRecommendations courses={courses} loadingCourses={loadingCourses} />

          <button onClick={generateRecommendations} disabled={loading} className="btn-secondary text-sm w-full">
            {loading ? (
              <span className="inline-flex items-center gap-2">
                <svg className="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                Regenerating...
              </span>
            ) : 'Regenerate'}
          </button>
        </div>
      )}
    </div>
  );
};

export default NextBestStep;
