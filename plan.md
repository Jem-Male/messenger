![alt](./florent-boston-mononokev1.jpg)

# Annotated - это говно!

```python
    @model_validator(mode='after')
    
    def check_at_least_ine_exists(self) -> Self:
        if not self.group_id or self.recipient_user_id:
            raise ValueError()
        return self
```
эту часть кода надо понять