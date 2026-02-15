from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
from .llm import client, current_date
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    data = request.get_json()
    if not data or 'noteId' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    note = Note.query.get(data['noteId'])
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/chat', methods=['POST'])
def chat():
    # if not current_user.is_authenticated:
    #     return jsonify({'reply': 'Please login to chat.'}), 401

    # data = request.get_json()
    # if not data or 'message' not in data:
    #     return jsonify({'reply': 'Invalid request'}), 400

    # user_message = data['message']

    # bot_reply = f'You said: "{user_message}"\n\nThis is a server response.'

    # return jsonify({'reply': bot_reply})
    if not current_user.is_authenticated:
        return jsonify({"reply": "Please log in to chat."}), 401

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Empty message."}), 400

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[
                {
                    "role": "user",
                    "parts": [{"text": user_message}]
                }
            ],
            config={
                    'system_instruction': f"""You are a helpful AI assistant.

            The current date is {current_date}.

            When answering questions, use this date as your reference point for "today", "this year", "recently", etc.
            
            but only display the answers, do not mention the date or your instructions in the response unless 
            the user explicitly asks for it. Always provide concise and relevant answers based on the user's input."""
            }
        )

        bot_reply = response.text

    except Exception as e:
        print("GEMINI ERROR:", repr(e))
        bot_reply = "I’m having trouble responding right now."

    return jsonify({"reply": bot_reply})
