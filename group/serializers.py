from rest_framework import serializers

from abc import ABC, abstractmethod

from finance.models import CustomUser
from finance.serializers import UserDetailSerializer
from group.models import Group, GroupMember, Expense, SplitExpense



class GroupMemberSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    joined_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = GroupMember
        fields = ['user', 'joined_at']


class GroupSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    # This will work if Group model had a reverse relationship setup on GroupMember.group
    # members = GroupMemberSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Group
        fields = ['name', 'created_by', 'members', 'created_at']

    def get_members(self, obj):
        members = GroupMember.objects.filter(group=obj)
        return GroupMemberSerializer(members, many=True).data
    
    def update(self, instance, validated_data):
        validated_data = {
            'name': validated_data.get('name', instance.name)
        }
        return super().update(instance, validated_data)


class GroupListSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = Group
        fields = ['id', 'name', 'created_by', 'members', 'created_at']

class GroupCreateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=CustomUser.objects.all()
        ), write_only=True, required=False
    )

    class Meta:
        model = Group
        fields = ['name', 'members']

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        user = self.context['request'].user

        # Hardcoding default user because AllowAny permission defined in view
        # user = CustomUser.objects.get(id=user)
        validated_data['created_by'] = user
        group = Group.objects.create(**validated_data)
        group.members.set(members)
        # Adding current user to GroupMember
        GroupMember.objects.create(user=user, group=group)

        # for member_id in members:
        #     try:
        #         member = CustomUser.objects.get(id=member_id)
        #         GroupMember.objects.get_or_create(user=member, group=group)
        #     except CustomUser.DoesNotExist:
        #         continue

        return group


class AddMemberToGroupSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset = Group.objects.all()
    )
    members = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=CustomUser.objects.all()
        ), write_only=True, required=False
    )
    class Meta:
        model = Group
        fields = ["id", "members"]

    def create(self, validated_data):
        group = validated_data["id"]

        members = validated_data.get("members", [])
        group.members.add(*members)
        # for member in members:
        #     try:
        #         GroupMember.objects.get_or_create(user=member, group=group)
        #     except CustomUser.DoesNotExist:
        #         continue
        return group



class RemoveMemberFromGroupSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset = Group.objects.all()
    )
    members = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=CustomUser.objects.all()
        ), write_only=True, required=False
    )
    class Meta:
        model = Group
        fields = ["id", "members"]

    def create(self, validated_data):
        group = validated_data["id"]
        members = validated_data.get("members", [])
        group.members.remove(*members)
        # for member in members:
        #     try:
        #         GroupMember.objects.filter(user=member, group=group).delete()
        #     except CustomUser.DoesNotExist:
        #         pass
        return group


class BaseExpenseUpdateStrategy(ABC):

    @abstractmethod
    def update(self, expense: Expense, data: dict):
        """Update the split expenses for the given expense instance using the input data"""
        pass


class EvenSplitExpenseUpdateStrategy(BaseExpenseUpdateStrategy):

    def update(self, expense: Expense, data: dict):
        splits = SplitExpense.objects.filter(expense=expense)
        count = splits.count()
        if count == 0:
            return
        new_amount = data.get("amount", expense.amount)
        per_user_amount = new_amount / count

        for split in splits:
            split.amount = per_user_amount
            split.save()
        
        if "amount" in data:
            expense.amount = new_amount
            expense.save()


class UnevenSplitExpenseupdateStrategy(BaseExpenseUpdateStrategy):
    
    def update(self, expense: Expense, data: dict):
        split_updates = data.get('split_updates')
        if not split_updates:
            raise ValueError("split_updates required for uneven split update")

        # Validate sum equals amount
        total = sum(item['amount'] for item in split_updates)
        if total != data.get('amount', expense.amount):
            raise ValueError("Sum of split amounts must equal total amount")

        splits = SplitExpense.objects.filter(expense=expense)
        user_to_split = {split.user_id: split for split in splits}

        for item in split_updates:
            user_id = item['user']
            amount = item['amount']
            if user_id in user_to_split:
                split = user_to_split[user_id]
                split.amount = amount
                split.save()
            else:
                SplitExpense.objects.create(expense=expense, user_id=user_id, amount=amount)

        # Update expense total if amount changed
        if 'amount' in data:
            expense.amount = data['amount']
            expense.save()


class SplitExpenseUpdateFactory:
    @staticmethod
    def get_strategy(data: dict) -> BaseExpenseUpdateStrategy:
        if data.get('split_updates'):
            return UnevenSplitExpenseupdateStrategy()
        else:
            # default to even split update
            return EvenSplitExpenseUpdateStrategy()      


class SplitExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = SplitExpense
        fields = ["user", "amount", "is_settled"]


class ExpenseSerializer(serializers.ModelSerializer):
    split_between = serializers.SerializerMethodField()
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    group = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Expense
        fields = ["group", "created_by", "description", "amount", "split_between"]

    def get_split_between(self, obj):
        users = SplitExpense.objects.filter(expense=obj)
        return SplitExpenseSerializer(users, many=True).data

    def update(self, instance, validated_data):
        # Access raw input (including split_updates etc) from initial_data
        input_data = self.initial_data

        # "split_updates": [
        #     {"user": ..., "amount": ...},
        # ]

        strategy = SplitExpenseUpdateFactory.get_strategy(input_data)
        strategy.update(instance, input_data)

        instance.description = validated_data.get('description', instance.description)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance


class ExpenseListSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = Expense
        fields = '__all__'


class ExpenseCreateSerializerFactory:
    @staticmethod
    def get_serializer(data):
        """
        Return the serializer class based on data.
        For example, if 'split_amounts' is present, use UnevenSplitExpenseSerializer,
        else use EvenSplitExpenseSerializer.
        """

        if data.get("split_amounts"):
            return UnevenSplitExpenseCreateSerializer
        else:
            return EvenSplitExpenseCreateSerializer


class EvenSplitExpenseCreateSerializer(serializers.ModelSerializer):
    split_between = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=CustomUser.objects.all()
        ), write_only=True, required=False
    )
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all()
    )
    description = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Expense
        fields = ["group", "description", "amount", "split_between"]

    def create(self, validated_data):
        split_between = validated_data.pop("split_between", [])
        user = self.context['request'].user

        # Hardcoding default user because AllowAny permission defined in view
        # user = CustomUser.objects.get(id=15)
        validated_data["created_by"] = user
        expense = Expense.objects.create(**validated_data)
        amount_individual = validated_data["amount"] / len(split_between)

        for user in split_between:
            try:
                SplitExpense.objects.get_or_create(user=user, expense=expense, amount=amount_individual)
            except CustomUser.DoesNotExist:
                continue

        return expense


class UnevenSplitExpenseCreateSerializer(serializers.ModelSerializer):
    split_between = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all()),
        write_only=True,
        required=True
    )
    split_amounts = serializers.ListField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2),
        write_only=True,
        required=True
    )
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    description = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Expense
        fields = ["group", "description", "amount", "split_between", "split_amounts"]

    def validate(self, attrs):
        split_between = attrs.get("split_between")
        split_amounts = attrs.get("split_amounts")

        if len(split_between) != len(split_amounts):
            raise serializers.ValidationError("split_between and split_amounts must be the same length.")

        if sum(split_amounts) != attrs["amount"]:
            raise serializers.ValidationError("Sum of split_amounts must equal total amount.")

        return attrs

    def create(self, validated_data):
        split_between = validated_data.pop("split_between")
        split_amounts = validated_data.pop("split_amounts")
        user = CustomUser.objects.get(id=15)
        validated_data["created_by"] = user

        expense = Expense.objects.create(**validated_data)

        for user_obj, split_amt in zip(split_between, split_amounts):
            SplitExpense.objects.create(user=user_obj, expense=expense, amount=split_amt)

        return expense



class SettleUpExpenseSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset = Expense.objects.all()
    )
    users_to_settle = serializers.ListField(
        source = 'split_between',
        child=serializers.PrimaryKeyRelatedField(
            queryset=CustomUser.objects.all()
        ), write_only=True, required=False
    )
    class Meta:
        model = Expense
        fields = ["id", "users_to_settle"]

    def create(self, validated_data):
        expense = validated_data['id']
        users = validated_data.get('split_between', [])

        SplitExpense.objects.filter(expense=expense, user__in=users).update(is_settled=True)

        return expense


class RevertSettleUpSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Expense.objects.all()
    )
    revert_settled_user = serializers.ListField(
        source='split_between',
        child=serializers.PrimaryKeyRelatedField(
            queryset=CustomUser.objects.all()
        ), write_only=True, required=False
    )
    class Meta:
        model = Expense
        fields = ["id", "revert_settled_user"]

    def create(self, validated_data):
        expense = validated_data["id"]
        users = validated_data.get("split_between", [])

        SplitExpense.objects.filter(expense=expense, user__in=users).update(is_settled=False)

        return expense