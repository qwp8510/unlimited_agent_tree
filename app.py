from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
# MySql datebase
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:root@localhost/unlimited_tree"

db = SQLAlchemy(app)

class Agent(db.Model):
    __tablename__ = 'agent'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    level = db.Column(db.Integer)
    left = db.Column(db.Integer)
    right = db.Column(db.Integer)

    def __init__(self, username, level, left, right):
        self.username = username
        self.level = level
        self.left = left
        self.right = right


class AgentService():
    def insert(self, parent, new_username):
        parent = Agent.query.filter_by(username=parent).first()
        level, left, right = parent.level, parent.left, parent.right
        new_level, new_left, new_right = level + 1, right, right + 1
        new_agent = Agent(new_username, new_level, new_left, new_right)
        # add new agent
        db.session.add(new_agent)
        # update left: l < l(now) & r >= l(now)  右+2
        db.session.query(Agent).filter(
            Agent.left < new_left,
            Agent.right >= new_left,
        ).update(
            {Agent.right: Agent.right + 2}
        )
        # update right: l > l(now) & r > r(now)  左右+2
        db.session.query(Agent).filter(
            Agent.left > new_left,
            Agent.right > new_right,
        ).update(
            {
                Agent.left: Agent.left + 2,
                Agent.right: Agent.right + 2
            }
        )
        db.session.commit()
        return {'parent': parent, 'agent': new_username, 'level': new_level, 'left': new_left, 'right': new_right}

    def remove(self, username):
        agent = Agent.query.filter_by(username=username).first()
        level, left, right = agent.level, agent.left, agent.right
        # delete agent
        db.session.delete(agent)
        # update left: l < l(now) & r >= l(now)  右-2
        db.session.query(Agent).filter(
            Agent.left < left,
            Agent.right >= left,
        ).update(
            {Agent.right: Agent.right - 2}
        )
        # update right: l > l(now) & r > r(now)  左右-2
        db.session.query(Agent).filter(
            Agent.left > left,
            Agent.right > right,
        ).update(
            {
                Agent.left: Agent.left - 2,
                Agent.right: Agent.right - 2
            }
        )
        db.session.commit()
        return {'agent': username, 'level': level, 'left': left, 'right': right}
    
    def get_childs(self, parent):
        result = []
        parent = Agent.query.filter_by(username=parent).first()
        for child in Agent.query.filter(and_(Agent.left > parent.left, Agent.right < parent.right)):
            result.append({
                'agent': child.username,
                'level': child.level,
                'left': child.left,
                'right': child.right,
            })
        return result
    
    def get_parent(self, child):
        child = Agent.query.filter_by(username=child).first()
        agent = Agent.query.filter(
            and_(Agent.left < child.left, Agent.right > child.right, Agent.level==child.level-1)).first()
        return {'agent': agent.username, 'level': agent.level, 'left': agent.left, 'right': agent.right}


agents = AgentService()

@app.route('/agent', methods=['POST'])
def insert():
    parent, new = request.json['parent'], request.json['agent']
    print(parent, new)
    result = agents.insert(parent, new)
    return jsonify(result)


@app.route('/agent', methods=['DELETE'])
def remove():
    agent = request.args.get('agent')
    print(agent)
    result = agents.remove(agent)
    return jsonify(result)


@app.route('/agent/child')
def agent_child():
    parent = request.args.get('parent')
    result = agents.get_childs(parent)
    print(result)
    return jsonify(result)


@app.route('/agent/parent')
def agent_parent():
    child = request.args.get('child')
    result = agents.get_parent(child)
    print(result)
    return jsonify(result)


@app.route('/init')
def init_data():
    """
             1'A'10
              /  \ 
           2'B'7  8'E'9
           /   \
         3'C'4 5'D'6
    """
    db.create_all()
    A = Agent('A', 1, 1, 10)
    B = Agent('B', 2, 2, 7)
    C = Agent('C', 3, 3, 4)
    D = Agent('D', 3, 5, 6)
    E = Agent('E', 2, 8, 9)
    db.session.add(A)
    db.session.add(B)
    db.session.add(C)
    db.session.add(D)
    db.session.add(E)
    db.session.commit()
    return 'ok'
    

if __name__ == '__main__':
    app.run(port=6666, debug=True)
