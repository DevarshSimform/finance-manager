from rest_framework import serializers

from finance.models import CustomUser
from group.models import Group, GroupMember



class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = ['user', 'joined_at']


class GroupSerializer(serializers.ModelSerializer):
    # members = serializers.SerializerMethodField()
    members = GroupMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = '__all__'

    # def get_members(self, obj):
    #     members = GroupMember.objects.filter(group=obj)
    #     return GroupMemberSerializer(members, many=True).data


class GroupCreateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Group
        fields = ['name', 'members']

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        # user = self.context['request'].user
        
        # Hardcoding default user because AllowAny permission defined in view
        user = CustomUser.objects.get(id=15)
        validated_data['created_by'] = user
        group = Group.objects.create(**validated_data)

        for member_id in members:
            try:
                member = CustomUser.objects.get(id=member_id)
                GroupMember.objects.create(user=member, group=group)
            except CustomUser.DoesNotExist:
                continue

        return group