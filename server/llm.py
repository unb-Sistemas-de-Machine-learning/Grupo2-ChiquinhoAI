from fastapi import FastAPI

class LLM:
    def __init__(self):
        self.app = FastAPI()

    def request(self, prompt, data):
        return f"Resposta simulada: [{prompt}] - usando {data}"