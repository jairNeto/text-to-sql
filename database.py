from supabase import create_client, Client
from message import Message, MessageFeedback

class SupabaseDB:
    def __init__(self, url: str, key: str):
        self.supabase: Client = create_client(url, key)

    def insert_feedback(self, message_feedback: MessageFeedback) -> None:
        self.supabase.table('MessageFeedback').insert(message_feedback.model_dump()).execute()

    def has_feedback(self, message_id: str) -> bool:
        data, _ = self.supabase.table('MessageFeedback').select('assistant_id').eq('assistant_id', message_id).execute()
        return len(data[1]) > 0

    def get_feedback(self, message_id: str):
        data, _ = self.supabase.table('MessageFeedback').select('was_helpful').eq('assistant_id', message_id).execute()
        return data[1][0]['was_helpful'] if data[1] else None

    def insert_message(self, message: Message, table_name: str = 'Message') -> None:
        self.supabase.table(table_name).insert(message.model_dump()).execute()
  
