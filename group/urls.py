from django.urls import path
from group import views

urlpatterns = [
    path('group/', views.GroupListCreateAPIView.as_view(), name="group_list_create"),
    path('group/<int:pk>/', views.GroupRetrieveUpdateDestroyAPIView.as_view(), name='group_retrieve_update_delete'),
    path('group/add/', views.AddMemberToGroup.as_view(), name="add_member_to_group"),
    path('group/remove/', views.RemoveMemberFromGroup.as_view(), name="add_member_from_remove"),
    path('expense/', views.ExpenseListCreateAPIView.as_view(), name="expense_list_create"),
    path('expense/<int:pk>/', views.ExpenseRetrieveUpdateDestroyAPIView.as_view(), name="expense_retrieve_update_destroy"),
    path('expense/settleup/', views.SettleUpExpenseAPIView.as_view(), name='settleup_expense'),
    path('expense/revert-settleup/', views.RevertSettleUpAPIView.as_view(), name='revert_settleup')

]
