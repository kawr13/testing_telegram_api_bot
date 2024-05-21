from datetime import timedelta

# Define the messages to send at each stage
MESSAGES = {
    'msg1': {
        'text': "Текст1",
        'delay': timedelta(minutes=1)
    },
    'msg2': {
        'text': "Текст2",
        'delay': timedelta(minutes=2),
        'trigger_check': True  # Whether to check for triggers before sending this message
    },
    'msg3': {
        'text': "Текст3",
        'delay': timedelta(days=1, hours=2)
    }
}

# Define the column names for message timestamps
MESSAGE_COLUMNS = ['msg1_sent_at', 'msg2_sent_at', 'msg3_sent_at']
