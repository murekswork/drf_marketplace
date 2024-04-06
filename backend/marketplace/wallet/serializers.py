from rest_framework import serializers

from .models import Wallet


def existing_wallet_validator(value):

    if Wallet.objects.filter(user=value).exists():
        raise serializers.ValidationError("You already have an existing wallet")
    return value


class WalletSerializer(serializers.ModelSerializer):

    default_validators = [existing_wallet_validator]
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    balance = serializers.DecimalField(read_only=True, max_digits=50, decimal_places=2)

    class Meta:
        model = Wallet
        fields = [
            "id",
            "user",
            "balance",
        ]

    def validate_user(self, user):
        for validator in self.default_validators:
            validator(user)
        return user

    def create(self, validated_data):
        user = self.context.get("request").user

        validated_data["user"] = self.validate_user(user)
        wallet = super().create(validated_data)
        return wallet
