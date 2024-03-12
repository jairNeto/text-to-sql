from pydantic import BaseModel, Field
import uuid
import datetime
# TODO: Melhor colocar conversationTurn

class Message(BaseModel):
    """
    Represents a message in a chat.

    Attributes:
        role: The role of the entity sending the message (e.g., 'user', 'assistant').
        content: The content of the message.
        id: A unique identifier for the message.
    """
    role: str
    content: str
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str


# class conversationTurn(BaseModel):
#     """
#     Represents a turn in a chat.

#     Attributes:
#         role: The role of the entity sending the message (e.g., 'user', 'assistant').
#         content: The content of the message.
#         id: A unique identifier for the message.
#     """
#     conversation_id: uuid.UUID = uuid.uuid4()
#     user_message: str
#     assistant_response: str
#     user_message_created_at: datetime.datetime
#     assistant_response_created_at: datetime.datetime
#     user_message_id: uuid.UUID = uuid.uuid4()
#     assistant_response_id: uuid.UUID = uuid.uuid4()


class MessageFeedback(BaseModel):
    """
    Represents feedback for a pair of user and model messages.

    Attributes:
        user_message: The user's message.
        model_response: The model's response to the user's message.
        feedback: A boolean indicating whether the feedback is positive or negative.
        feedback_content: Additional content or explanation for the feedback.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    assistant_id: str
    user_message: str
    model_response: str
    was_helpful: bool
    feedback_content: str
