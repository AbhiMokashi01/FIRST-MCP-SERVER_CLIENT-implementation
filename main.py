import os
from dotenv import load_dotenv
from llm import model
import json

def main():
    
    result=model.invoke("Explain Python decorators to a beginner.")
    print(result.content)
    
    

if __name__=="__main__":
    main()
