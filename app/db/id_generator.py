from snowflake import SnowflakeGenerator

class IDGenerator:
    _instance = None
    _generator = None
    
    def __new__(cls, instance_id: int = 1):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._generator = SnowflakeGenerator(instance=instance_id)
        return cls._instance
    
    def generate(self) -> int:
        return next(self._generator)

id_generator = IDGenerator()