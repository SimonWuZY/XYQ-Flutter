from utils import *

if __name__ == "__main__":
    question = input("请输入：\n")
    #results = work_flow(question, True)
    results = workflow(question)
    #results = prompt_LLM(question)

    print(results)
