from rest_framework import serializers

from group.models import Group, GroupMember



class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = ['user', 'joined_at']

class GroupSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = '__all__'

    def get_members(self, obj):
        members = GroupMember.objects.filter(group=obj)
        return GroupMemberSerializer(members, many=True).data