import pytest
from django.core.exceptions import ValidationError
from bot_settings.models import BotConfig

@pytest.mark.django_db
class TestBotConfigHardening:
    def test_singleton_load_and_save(self):
        """Verify that load() returns a singleton with PK=1."""
        config = BotConfig.load()
        assert config.pk == 1
        
        config2 = BotConfig.load()
        assert config2.pk == 1
        assert config == config2
        
        # Even if we try to create another one with save(), it should force PK=1
        new_config = BotConfig(admin_chat_id="12345")
        new_config.save()
        assert new_config.pk == 1
        assert BotConfig.objects.count() == 1

    def test_prevent_instance_delete(self):
        """Verify that calling .delete() on an instance raises ValidationError."""
        config = BotConfig.load()
        with pytest.raises(ValidationError, match="This configuration cannot be deleted."):
            config.delete()
        
        # Verify it still exists
        assert BotConfig.objects.filter(pk=1).exists()

    def test_prevent_bulk_delete(self):
        """Verify that calling .delete() on a queryset raises ValidationError."""
        BotConfig.load()
        with pytest.raises(ValidationError, match="This configuration cannot be deleted."):
            BotConfig.objects.all().delete()
        
        # Verify it still exists
        assert BotConfig.objects.count() == 1
