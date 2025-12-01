"""
URL configuration for stories app
"""
from django.urls import path
from . import views

app_name = 'stories'

urlpatterns = [
    # Homepage and collaborative stories
    path('', views.homepage, name='homepage'),
    path('create-story/', views.create_story_pitch, name='create_story_pitch'),
    path('story/<slug:slug>/', views.story_detail, name='story_detail'),
    path('story/<slug:slug>/chapter/<int:chapter_number>/', views.chapter_detail, name='chapter_detail'),
    path('story/<slug:slug>/chapter/<int:chapter_number>/edit/', views.edit_chapter, name='edit_chapter'),
    path('story/<slug:slug>/chapter/<int:chapter_number>/comment/', views.add_comment, name='add_comment'),
    path('story/<slug:slug>/submit-prompt/', views.submit_prompt, name='submit_prompt'),
    path('story/<slug:slug>/subscribe/', views.subscribe_story, name='subscribe_story'),
    path('story/<slug:slug>/upvote/', views.upvote_story, name='upvote_story'),
    path('prompt/<int:prompt_id>/vote/', views.vote_prompt, name='vote_prompt'),

    # Personal stories
    path('my-stories/', views.my_stories, name='my_stories'),
    path('create-personal-story/', views.create_personal_story, name='create_personal_story'),
    path('personal/<slug:slug>/continue/', views.continue_personal_story, name='continue_personal_story'),
    path('personal/<slug:slug>/publish/', views.publish_story, name='publish_story'),
    path('story/<slug:slug>/mark-complete/', views.mark_complete, name='mark_complete'),
    path('story/<slug:slug>/publish-to-community/', views.publish_to_community, name='publish_to_community'),
    path('story/<slug:slug>/delete/', views.delete_story, name='delete_story'),

    # Cover image generation
    path('generate-cover/', views.generate_cover_image, name='generate_cover_image'),

    # Credits
    path('credits/', views.credits_dashboard, name='credits_dashboard'),

    # Feedback
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('feedback/admin/', views.feedback_admin, name='feedback_admin'),

    # Beta Mode
    path('admin/beta/', views.toggle_beta_mode, name='toggle_beta_mode'),
]
