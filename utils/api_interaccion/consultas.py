
import json, os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

""" assistant = client.beta.assistants.retrieve("asst_LMnzwqHscAlIEBRRrWzB6myW")
print(assistant.tools) """

""" messages = client.beta.threads.messages.list(thread_id="thread_5kaLyMXKuPKvyIKWVCt60bK8", limit=100)

messages = [msg.model_dump() for msg in messages]

with open("salida_corrupta.json", 'w', encoding='utf-8') as f:
    messages = json.dump(messages, f, indent=2, ensure_ascii=False) """

# client.beta.threads.messages.delete(message_id="msg_KY1JoK0SJG7o5ED1FChvN8r7", thread_id="thread_5kaLyMXKuPKvyIKWVCt60bK8")

""" archivos = client.vector_stores.files.list(vector_store_id='vs_68f26703b2dc819188bec821c21e8198')

temas = [tema.model_dump() for tema in archivos]

with open('preguntas_com_est.json', mode='w', encoding='utf-8') as f:
    temas = json.dump(temas, f, indent=2, ensure_ascii=False) """

""" ASSISTANT_ID = "asst_wcrHOLOst1B87ZQegR5mRnBU"

a = client.beta.assistants.retrieve(ASSISTANT_ID)
print(a.tools) """


ASSISTANT_ID = "asst_wcrHOLOst1B87ZQegR5mRnBU"

assistant = client.beta.assistants.update(
    assistant_id=ASSISTANT_ID,
    tools=[
        # 1) Code Interpreter (tal como aparece en tu assistant actual)
        {
            "type": "code_interpreter"
        },

        # 2) File Search con tuning de ranking_options
        {
            "type": "file_search",
            "file_search": {
                "max_num_results": 12,

                "ranking_options": {
                    "score_threshold": 0.6,
                    "ranker": "default_2024_08_21",
                }
            }
        },

        # 3) Función: iniciar_evaluacion
        {
            "type": "function",
            "function": {
                "name": "iniciar_evaluacion",
                "description": "Inicia una evaluación para el estudiante sobre un tema específico.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tema": {
                            "type": "string",
                            "description": "El nombre del tema o materia sobre la cual se debe realizar la evaluación."
                        },
                        "num_questions": {
                            "type": "integer",
                            "description": "El número de preguntas para la evaluación. Por defecto es 5."
                        }
                    },
                    "required": ["tema"]
                },
                "strict": False
            }
        },

        # 4) Función: calificar_evaluacion
        {
            "type": "function",
            "function": {
                "name": "calificar_evaluacion",
                "description": ("Se llama cuando el usuario indica que ha terminado su evaluación "
                                "y envía sus respuestas. Inicia el proceso de calificación para "
                                "la evaluación activa."),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "evaluation_id": {
                            "type": "integer",
                            "description": ("El ID de la evaluación que se está calificando, "
                                            "inferido del contexto de la conversación.")
                        }
                    },
                    "required": ["evaluation_id"]
                },
                "strict": False
            }
        }
    ],
)

print("Assistant actualizado correctamente.")
print("Tools actuales:")
for tool in assistant.tools:
    print(tool)
