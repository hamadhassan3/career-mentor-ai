
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ResumeListCreateView.as_view(), name='resume-list-create'),
    path('<int:pk>/', views.ResumeDetailView.as_view(), name='resume-detail'),
    path('<int:pk>/activate/', views.activate_resume, name='resume-activate'),
    path('upload/', views.create_resume_from_upload, name='resume-upload'),
    path('latest/', views.get_latest_resume, name='resume-latest'),
    path('active/', views.get_active_resume, name='resume-active'),
    
    # Next Best Step endpoints
    path('next-step/', views.get_next_best_step, name='get-next-step'),
    path('next-step/save/', views.save_next_best_step, name='save-next-step'),
    
    # Career Pathway endpoints
    path('career-pathway/', views.get_career_pathway, name='get-career-pathway'),
    path('career-pathway/save/', views.save_career_pathway, name='save-career-pathway'),
    
    # Clear recommendations
    path('recommendations/clear/', views.clear_recommendations, name='clear-recommendations'),
    
    # Course recommendations
    path('courses/', views.get_course_recommendations, name='get-course-recommendations'),
]