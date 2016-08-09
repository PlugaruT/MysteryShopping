
def update_attributes(validated_data, instance):
    for attr, value in validated_data.items():
        setattr(instance, attr, value)
    instance.save()
