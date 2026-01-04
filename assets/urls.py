from django.urls import path
from assets import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('purchases/', views.purchases, name='purchases'),
    path('purchases/<int:purchase_id>/approve/', views.approve_purchase, name='approve_purchase'),
    path('purchases/<int:purchase_id>/delete/', views.delete_purchase, name='delete_purchase'),
    path('transfers/', views.transfers, name='transfers'),
    path('transfers/<int:transfer_id>/approve/', views.approve_transfer, name='approve_transfer'),
    path('transfers/<int:transfer_id>/complete/', views.complete_transfer, name='complete_transfer'),
    path('transfers/<int:transfer_id>/delete/', views.delete_transfer, name='delete_transfer'),
    path('assignments/', views.assignments, name='assignments'),
    path('assignments/<int:assignment_id>/return/', views.return_assignment, name='return_assignment'),
    path('assignments/<int:assignment_id>/delete/', views.delete_assignment, name='delete_assignment'),
    path('expenditures/', views.expenditures, name='expenditures'),
    path('expenditures/<int:expenditure_id>/delete/', views.delete_expenditure, name='delete_expenditure'),
    path('assets/<int:asset_id>/', views.asset_detail, name='asset_detail'),
    path('assets/<int:asset_id>/net-movement/', views.net_movement_detail, name='net_movement_detail'),
    path('transactions/', views.transaction_log, name='transaction_log'),
]
