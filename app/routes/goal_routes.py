from flask import Blueprint, request, jsonify
from app.models.goal import Goal
from app.models.task import Task
from app import db
from app.routes.helper import validate_model


goals_bp = Blueprint("goals", __name__, url_prefix="/goals")


@goals_bp.route("", methods=["POST"])
def create_goal():
    goal_data = request.get_json()
    try:
        new_goal = Goal.from_dict(goal_data)

    except KeyError:
        message = {"details": "Invalid data"}
        return jsonify(message), 400

    db.session.add(new_goal)
    db.session.commit()

    result = {"goal": new_goal.to_dict()}
    return jsonify(result), 201


@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_tasks_for_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    response = request.get_json()
    for task_id in response["task_ids"]:
        task = validate_model(Task, task_id)
        task.goal_id = goal.goal_id

    db.session.commit()
    task_ids_list = [task.task_id for task in goal.tasks]

    result = {
        "id": goal.goal_id,
        "task_ids": task_ids_list
    }
    return jsonify(result), 200


@goals_bp.route("", methods=["GET"])
def get_all_goals():
    all_goals = Goal.query.all()
    goals_reponse = [goal.to_dict() for goal in all_goals]

    return jsonify(goals_reponse), 200


@goals_bp.route("/<goal_id>", methods=["GET"])
def get_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    result = {"goal": goal.to_dict()}
    return jsonify(result), 200


@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_of_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    tasks = Task.query.filter_by(goal_id=goal.goal_id)
    tasks_response = [task.to_dict() for task in tasks]

    result = {
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": tasks_response
    }

    return jsonify(result), 200


@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    response = request.get_json()
    goal_to_update = validate_model(Goal, goal_id)

    try:
        goal_to_update.title = response["title"]
    except KeyError:
        message = {"details": "Invalid data"}
        return jsonify(message), 400

    db.session.commit()

    result = {"goal": goal_to_update.to_dict()}
    return jsonify(result), 200


@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal_to_delete = validate_model(Goal, goal_id)
    db.session.delete(goal_to_delete)
    db.session.commit()

    message = {
        "details": f'Goal {goal_to_delete.goal_id} "{goal_to_delete.title}" successfully deleted'}
    return jsonify(message), 200
