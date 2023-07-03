#!/usr/bin/env python3

from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate

from models import db, Hero, Power, HeroPower

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    hero_list = []
    for hero in heroes:
        heroes_data = {
            'id': hero.id,
            'name': hero.name,
            'super_name': hero.super_name
        }
        hero_list.append(heroes_data)
    return jsonify(hero_list)

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if hero is None:
        return jsonify({'error': 'Hero not found'}), 404
    powers_data = []
    for power in hero.powers:
        powers_data.append({
            'id': power.id,
            'name': power.name,
            'description': power.description
        })
    hero_data = {
        'id': hero.id,
        'name': hero.name,
        'super_name': hero.super_name,
        'powers': powers_data
    }
    return jsonify(hero_data)

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    powers_data = []
    for power in powers:
        powers_data.append({
            'id': power.id,
            'name': power.name,
            'description': power.description
        })
    return jsonify(powers_data)

@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = Power.query.get(id)
    if power is None:
        return jsonify({'error': 'Power not found'}), 404
    power_data = {
        'id': power.id,
        'name': power.name,
        'description': power.description,
    }
    return jsonify(power_data)

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_powers(id):
    power = Power.query.get(id)
    if power is None:
        return jsonify({'error': 'Power not found'}), 404
    data = request.get_json()
    if 'description' not in data:
        return jsonify({'error': 'Description not provided'}), 400
    power.description = data['description']
    try:
        db.session.commit()
        return jsonify({
            'id': power.id,
            'name': power.name,
            'description': power.description
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    if 'strength' not in data or 'power_id' not in data or 'hero_id' not in data:
        return jsonify({'error': 'Missing required data'}), 400
    strength = data['strength']
    power_id = data['power_id']
    hero_id = data['hero_id']
    power = Power.query.get(power_id)
    hero = Hero.query.get(hero_id)
    if power is None or hero is None:
        return jsonify({'error': 'Power or Hero not found'}), 404
    hero_power = HeroPower(strength=strength, power=power, hero=hero)
    db.session.add(hero_power)
    try:
        db.session.commit()
        powers_data = []
        for power in hero.powers:
            powers_data.append({
                'id': power.id,
                'name': power.name,
                'description': power.description
            })
        hero_data = {
            'id': hero.id,
            'name': hero.name,
            'super_name': hero.super_name,
            'powers': powers_data
        }
        return jsonify(hero_data)
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5555)
