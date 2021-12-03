from django.urls import path
from . import views

app_name = 'dashboard'


urlpatterns = [
    path('', views.ProjectListView.as_view(), name='projects-list'),
    path('project/add-datetime-and-role/<str:title>/<int:pk>/', views.AddProjectDateAndRole.as_view(), # ok
         name='add-project-date-role'),
    path('project/add-crew-in-role/<str:title>/<int:project_id>/<int:role_id>/', views.AddCrewInRoleView.as_view(), name='add-crew-in-role'), # ok

    path('pending-projects/', views.PendingProjectView.as_view(), name='pending-projects'), # Ok
    path('completed-projects/', views.CompletedProjectView.as_view(), name='completed-projects'), # Ok
    path('project-approve/<int:pk>/', views.ProjectApproveApiView.as_view(), name='project-approve'), # Ok
    path('project-request-accept/<int:pk>/', views.ProjectRequestAcceptApiView.as_view(), name='project-request-accept'),  # Ok
    path('approved-projects/', views.ApprovedProjectView.as_view(), name='approved-projects'), # Ok
    path('project-delete/<int:pk>/', views.ProjectDeleteApiView.as_view(), name='project-delete'), # Ok
    path('project/add/', views.CreateProjectView.as_view(), name='project-add'), # Ok
    path('project/detail/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'), #Ok
    path('project/update/<int:pk>/', views.ProjectUpdateView.as_view(), name='project-update'), #Ok
    path('project-file/delete/<int:pk>/', views.AttachFileDeleteApiView.as_view(), name='file-delete'), # Ok

]
