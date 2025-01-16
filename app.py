from datetime import datetime
from flask import Flask, request, jsonify
from models.task import Task
import requests
from dotenv import load_dotenv
import os


app = Flask(__name__)


tasks = []
task_id_control = 1

@app.route('/alunos/<int:matricula>', methods=['GET'])
def alunos(matricula):
    auth = os.getenv("BASIC_AUTH")
    
    if len(str(matricula)) < 7:
        url = f"https://evo-integracao-api.w12app.com.br/api/v1/members/{matricula}"
        headers = {
        "accept": "application/json",
        "authorization":auth
    }
    else:
        url = f"https://evo-integracao.w12app.com.br/api/v1/members?document={matricula}"        
        headers = {
        "accept": "application/json",
        "authorization":auth
        }
    

    response = requests.get(url, headers=headers)
    
    alunoa=response.json()
    if isinstance(alunoa, list):
        aluno=alunoa[0]
    elif isinstance(alunoa, dict):
        aluno=alunoa    
    
    
    #gympass
    
    if aluno["membershipStatus"] == "Inactive":
        url = f"https://evo-integracao.w12app.com.br/api/v1/members?take=50&skip=0&idsMembers={matricula}&onlyPersonal=false&showActivityData=false"        
        headers = {
        "accept": "application/json",
        "authorization":auth
        }
        responseGym = requests.get(url, headers=headers)
        alunoGymtudo=responseGym.json()
        alunogymPass = [a['gympassId'] for a in alunoGymtudo]
        
    plano = [n["name"] for n in aluno["memberships"] if n["membershipStatus"] == "active"]    
    
    # Filtrando planos ativos e formatando a data 'endDate'
    vencimento_plano = [
        datetime.strptime(n["endDate"], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y")
        for n in aluno["memberships"]
        if n["membershipStatus"] == "active"
    ]
    
    
   # Criando o dicionário 'student'
    aluno["photo"] = aluno["photo"] if aluno.get("photo") else aluno.get("photoUrl")
    student = {    
    "photo": aluno["photo"],
    "name": aluno["firstName"],
    "status": aluno["membershipStatus"],
    "registration": aluno["idMember"],
    "endDate": ''.join(vencimento_plano),  
    "plano": ''.join(plano)
    }
    
    if not aluno["idMember"]:
        return jsonify({'message': 'Aluno não encontrado'}), 404 
    
    if aluno["membershipStatus"] == "Inactive" and (alunogymPass[0] is None if alunogymPass else False): 
        print('entrou')
        return jsonify({'message': "Seu plano está Inativo | Favor procurar recepção"}), 200 
    
    return student
    
@app.route('/historico/<int:matricula>', methods=['GET'])
def historico(matricula):
    return str(matricula)    

    

    

@app.route('/tasks', methods=['POST'])
def create_task():
    global task_id_control
    data = request.get_json()
    new_task = Task(id=task_id_control, title=data['title'], description=data.get('description', ''))
    task_id_control += 1
    tasks.append(new_task)
    print(tasks)
    return jsonify({'message': 'Criada com sucesso'})

@app.route('/tasks', methods=['GET'])
def get_tasks():
     task_list = [task.to_dict() for task in tasks]
     output = {
            "tasks": task_list,
            "total_tasks": len(task_list)
    }
     return jsonify(output)

@app.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    task = None
    for t in tasks:
        if t.id == id:
            return jsonify(t.to_dict())
    return jsonify({'message': 'Não encontrada'}), 404  

@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = None
    for t in tasks:
        if t.id == id:
            task = t
        if task == None:
            return jsonify({'message': 'Não encontrada'}), 404    

        data = request.get_json()
        task.title = data['title']
        task.description = data.get('description')
        task.completed = data.get('completed')
        return jsonify({'message': 'Atualizada com sucesso'})

@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = None
    for t in tasks:
        if t.id == id:
            task = t
    if task == None:
        return jsonify({'message': 'Não encontrada'}), 404
    tasks.remove(task)
    return jsonify({'message': 'Removida com sucesso'})


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)    