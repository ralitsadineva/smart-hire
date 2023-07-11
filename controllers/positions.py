from flask import render_template, request, redirect, session
import services.positions as position_service

def positions():
    positions = position_service.get_all()
    return render_template('positions.html', positions=positions, avatar=session['avatar'])

def add_position():
    if request.method == 'POST':
        result = position_service.add(session['user_id'], request.form['title'], request.form['description'])
        if result['success']:
            return redirect('/positions')
        else:
            return render_template('add_position.html', **result['error'], avatar=session['avatar'])
    else:
        return render_template('add_position.html', avatar=session['avatar'])

def duplicate_position(position_id):
    if request.method == 'POST':
        result = position_service.add(session['user_id'], request.form['title'], request.form['description'])
        if result['success']:
            return redirect('/positions')
        else:
            position = position_service.duplicate(position_id)
            return render_template('add_position.html', position=position, **result['error'], avatar=session['avatar'])
    else:
        position = position_service.duplicate(position_id)
        return render_template('add_position.html', position=position, avatar=session['avatar'])

def positions_history():
    positions = position_service.history()
    return render_template('positions_history.html', positions=positions, avatar=session['avatar'])

def position(position_id):
    result = position_service.get(position_id)
    return render_template('position.html', **result, avatar=session['avatar'])

def edit_position(position_id):
    if request.method == 'POST':
        result = position_service.edit(position_id, request.form['title'], request.form['description'])
        if result['success']:
            return redirect('/positions')
        else:
            return render_template('edit_position.html', **result['error'], position=result['position'], avatar=session['avatar'])
    else:
        position = position_service.get(position_id)['position']
        return render_template('edit_position.html', position=position, avatar=session['avatar'])

def archive_position(position_id):
    position_service.archive(position_id)
    return redirect('/positions')

def activate_position(position_id):
    position_service.activate(position_id)
    return redirect('/positions')
