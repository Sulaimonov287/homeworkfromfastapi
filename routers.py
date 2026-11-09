from fastapi import FastAPI, APIRouter, HTTPException
from datetime import datetime, timedelta

app = FastAPI(title='MedBook API')
router = APIRouter(prefix='/api/v1')

specializations = []
doctors = []
patients = []
appointments = []

spec_next_id = 0
doctor_next_id = 0
patient_next_id = 0
appointment_next_id = 0


@router.post('/specializations')
async def create_specialization(name: str, description: str = None):
    global spec_next_id
    name = name.strip()
    if len(name) < 2 or len(name) > 100:
        raise HTTPException(422, 'Название должно быть от 2 до 100 символов!')
    for spec in specializations:
        if spec['name'].lower() == name.lower():
            raise HTTPException(409, 'Такая специализация уже есть!')
    spec_next_id += 1
    new_spec = {'id': spec_next_id, 'name': name, 'description': description}
    specializations.append(new_spec)
    return new_spec


@router.get('/specializations')
async def get_specializations():
    return specializations


@router.get('/specializations/{specialization_id}')
async def get_specialization(specialization_id: int):
    for spec in specializations:
        if spec['id'] == specialization_id:
            return spec
    raise HTTPException(404, 'Специализация не найдена!')


@router.patch('/specializations/{specialization_id}')
async def update_specialization(specialization_id: int, name: str = None, description: str = None):
    for spec in specializations:
        if spec['id'] == specialization_id:
            if name is not None:
                name = name.strip()
                if len(name) < 2 or len(name) > 100:
                    raise HTTPException(422, 'Название должно быть от 2 до 100 символов!')
                for other in specializations:
                    if other['name'].lower() == name.lower() and other['id'] != specialization_id:
                        raise HTTPException(409, 'Такая специализация уже есть!')
                spec['name'] = name
            if description is not None:
                spec['description'] = description
            return spec
    raise HTTPException(404, 'Специализация не найдена!')


@router.delete('/specializations/{specialization_id}')
async def delete_specialization(specialization_id: int):
    for spec in specializations:
        if spec['id'] == specialization_id:
            for doctor in doctors:
                if doctor['specialization_id'] == specialization_id:
                    raise HTTPException(409, 'К специализации привязаны врачи, удалить нельзя!')
            specializations.remove(spec)
            return {'message': 'Специализация удалена!'}
    raise HTTPException(404, 'Специализация не найдена!')


@router.post('/doctors')
async def create_doctor(full_name: str, specialization_id: int, experience_years: int,
                        consultation_price: float, is_active: bool = True):
    global doctor_next_id
    full_name = full_name.strip()
    if len(full_name) < 3 or len(full_name) > 100:
        raise HTTPException(422, 'Имя должно быть от 3 до 100 символов!')
    spec_found = False
    for spec in specializations:
        if spec['id'] == specialization_id:
            spec_found = True
    if spec_found == False:
        raise HTTPException(404, 'Специализация не найдена!')
    if experience_years < 0:
        raise HTTPException(422, 'Стаж не может быть отрицательным!')
    if consultation_price <= 0:
        raise HTTPException(422, 'Цена должна быть больше нуля!')
    doctor_next_id += 1
    new_doctor = {
        'id': doctor_next_id,
        'full_name': full_name,
        'specialization_id': specialization_id,
        'experience_years': experience_years,
        'consultation_price': consultation_price,
        'is_active': is_active
    }
    doctors.append(new_doctor)
    return new_doctor


@router.get('/doctors')
async def get_doctors(specialization_id: int = None, is_active: bool = None,
                      min_experience: int = None, max_price: float = None, search: str = None):
    result = []
    for doctor in doctors:
        if specialization_id is not None and doctor['specialization_id'] != specialization_id:
            continue
        if is_active is not None and doctor['is_active'] != is_active:
            continue
        if min_experience is not None and doctor['experience_years'] < min_experience:
            continue
        if max_price is not None and doctor['consultation_price'] > max_price:
            continue
        if search is not None and search.lower() not in doctor['full_name'].lower():
            continue
        result.append(doctor)
    return result


@router.get('/doctors/{doctor_id}')
async def get_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor['id'] == doctor_id:
            return doctor
    raise HTTPException(404, 'Врач не найден!')


@router.put('/doctors/{doctor_id}')
async def replace_doctor(doctor_id: int, full_name: str, specialization_id: int,
                         experience_years: int, consultation_price: float, is_active: bool = True):
    for doctor in doctors:
        if doctor['id'] == doctor_id:
            full_name = full_name.strip()
            if len(full_name) < 3 or len(full_name) > 100:
                raise HTTPException(422, 'Имя должно быть от 3 до 100 символов!')
            spec_found = False
            for spec in specializations:
                if spec['id'] == specialization_id:
                    spec_found = True
            if spec_found == False:
                raise HTTPException(404, 'Специализация не найдена!')
            if experience_years < 0:
                raise HTTPException(422, 'Стаж не может быть отрицательным!')
            if consultation_price <= 0:
                raise HTTPException(422, 'Цена должна быть больше нуля!')
            doctor['full_name'] = full_name
            doctor['specialization_id'] = specialization_id
            doctor['experience_years'] = experience_years
            doctor['consultation_price'] = consultation_price
            doctor['is_active'] = is_active
            return doctor
    raise HTTPException(404, 'Врач не найден!')


@router.patch('/doctors/{doctor_id}')
async def update_doctor(doctor_id: int, full_name: str = None, specialization_id: int = None,
                        experience_years: int = None, consultation_price: float = None,
                        is_active: bool = None):
    for doctor in doctors:
        if doctor['id'] == doctor_id:
            if full_name is not None:
                full_name = full_name.strip()
                if len(full_name) < 3 or len(full_name) > 100:
                    raise HTTPException(422, 'Имя должно быть от 3 до 100 символов!')
                doctor['full_name'] = full_name
            if specialization_id is not None:
                spec_found = False
                for spec in specializations:
                    if spec['id'] == specialization_id:
                        spec_found = True
                if spec_found == False:
                    raise HTTPException(404, 'Специализация не найдена!')
                doctor['specialization_id'] = specialization_id
            if experience_years is not None:
                if experience_years < 0:
                    raise HTTPException(422, 'Стаж не может быть отрицательным!')
                doctor['experience_years'] = experience_years
            if consultation_price is not None:
                if consultation_price <= 0:
                    raise HTTPException(422, 'Цена должна быть больше нуля!')
                doctor['consultation_price'] = consultation_price
            if is_active is not None:
                doctor['is_active'] = is_active
            return doctor
    raise HTTPException(404, 'Врач не найден!')


@router.delete('/doctors/{doctor_id}')
async def delete_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor['id'] == doctor_id:
            for item in appointments:
                if item['doctor_id'] == doctor_id:
                    raise HTTPException(409, 'У врача есть записи, удалить нельзя!')
            doctors.remove(doctor)
            return {'message': 'Врач удалён!'}
    raise HTTPException(404, 'Врач не найден!')


@router.post('/patients')
async def create_patient(full_name: str, phone: str, email: str = None, birth_date: str = None):
    global patient_next_id
    full_name = full_name.strip()
    if len(full_name) < 3 or len(full_name) > 100:
        raise HTTPException(422, 'Имя должно быть от 3 до 100 символов!')
    phone = phone.strip()
    if len(phone) < 1 or len(phone) > 30:
        raise HTTPException(422, 'Телефон должен быть от 1 до 30 символов!')
    if email is not None and '@' not in email:
        raise HTTPException(422, 'Неверный email!')
    if birth_date is not None:
        try:
            born = datetime.strptime(birth_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(422, 'Дату нужно писать так: 2002-05-12')
        if born > datetime.now():
            raise HTTPException(422, 'Дата рождения не может быть в будущем!')
    patient_next_id += 1
    new_patient = {
        'id': patient_next_id,
        'full_name': full_name,
        'phone': phone,
        'email': email,
        'birth_date': birth_date
    }
    patients.append(new_patient)
    return new_patient


@router.get('/patients')
async def get_patients(search: str = None):
    result = []
    for patient in patients:
        if search is not None and search.lower() not in patient['full_name'].lower():
            continue
        result.append(patient)
    return result


@router.get('/patients/{patient_id}')
async def get_patient(patient_id: int):
    for patient in patients:
        if patient['id'] == patient_id:
            return patient
    raise HTTPException(404, 'Пациент не найден!')


@router.put('/patients/{patient_id}')
async def replace_patient(patient_id: int, full_name: str, phone: str,
                          email: str = None, birth_date: str = None):
    for patient in patients:
        if patient['id'] == patient_id:
            full_name = full_name.strip()
            if len(full_name) < 3 or len(full_name) > 100:
                raise HTTPException(422, 'Имя должно быть от 3 до 100 символов!')
            phone = phone.strip()
            if len(phone) < 1 or len(phone) > 30:
                raise HTTPException(422, 'Телефон должен быть от 1 до 30 символов!')
            if email is not None and '@' not in email:
                raise HTTPException(422, 'Неверный email!')
            if birth_date is not None:
                try:
                    born = datetime.strptime(birth_date, '%Y-%m-%d')
                except ValueError:
                    raise HTTPException(422, 'Дату нужно писать так: 2002-05-12')
                if born > datetime.now():
                    raise HTTPException(422, 'Дата рождения не может быть в будущем!')
            patient['full_name'] = full_name
            patient['phone'] = phone
            patient['email'] = email
            patient['birth_date'] = birth_date
            return patient
    raise HTTPException(404, 'Пациент не найден!')


@router.patch('/patients/{patient_id}')
async def update_patient(patient_id: int, full_name: str = None, phone: str = None,
                         email: str = None, birth_date: str = None):
    for patient in patients:
        if patient['id'] == patient_id:
            if full_name is not None:
                full_name = full_name.strip()
                if len(full_name) < 3 or len(full_name) > 100:
                    raise HTTPException(422, 'Имя должно быть от 3 до 100 символов!')
                patient['full_name'] = full_name
            if phone is not None:
                phone = phone.strip()
                if len(phone) < 1 or len(phone) > 30:
                    raise HTTPException(422, 'Телефон должен быть от 1 до 30 символов!')
                patient['phone'] = phone
            if email is not None:
                if '@' not in email:
                    raise HTTPException(422, 'Неверный email!')
                patient['email'] = email
            if birth_date is not None:
                try:
                    born = datetime.strptime(birth_date, '%Y-%m-%d')
                except ValueError:
                    raise HTTPException(422, 'Дату нужно писать так: 2002-05-12')
                if born > datetime.now():
                    raise HTTPException(422, 'Дата рождения не может быть в будущем!')
                patient['birth_date'] = birth_date
            return patient
    raise HTTPException(404, 'Пациент не найден!')


@router.delete('/patients/{patient_id}')
async def delete_patient(patient_id: int):
    for patient in patients:
        if patient['id'] == patient_id:
            for item in appointments:
                if item['patient_id'] == patient_id:
                    raise HTTPException(409, 'У пациента есть записи, удалить нельзя!')
            patients.remove(patient)
            return {'message': 'Пациент удалён!'}
    raise HTTPException(404, 'Пациент не найден!')


@router.post('/appointments')
async def create_appointment(patient_id: int, doctor_id: int, start_at: str,
                             duration_minutes: int, reason: str = None):
    global appointment_next_id

    patient_found = False
    for patient in patients:
        if patient['id'] == patient_id:
            patient_found = True
    if patient_found == False:
        raise HTTPException(404, 'Пациент не найден!')

    found_doctor = None
    for doctor in doctors:
        if doctor['id'] == doctor_id:
            found_doctor = doctor
    if found_doctor is None:
        raise HTTPException(404, 'Врач не найден!')
    if found_doctor['is_active'] == False:
        raise HTTPException(409, 'Врач сейчас не принимает записи!')

    if duration_minutes not in [15, 30, 45, 60]:
        raise HTTPException(422, 'Длительность должна быть 15, 30, 45 или 60 минут!')

    try:
        start = datetime.strptime(start_at, '%Y-%m-%d %H:%M')
    except ValueError:
        raise HTTPException(422, 'Время нужно писать так: 2026-12-01 10:00')
    if start <= datetime.now():
        raise HTTPException(422, 'Время приёма должно быть в будущем!')

    new_end = start + timedelta(minutes=duration_minutes)
    for item in appointments:
        if item['doctor_id'] == doctor_id and item['status'] == 'scheduled':
            item_end = item['start_at'] + timedelta(minutes=item['duration_minutes'])
            if start < item_end and item['start_at'] < new_end:
                raise HTTPException(409, 'У врача уже есть запись на это время!')

    appointment_next_id += 1
    new_appointment = {
        'id': appointment_next_id,
        'patient_id': patient_id,
        'doctor_id': doctor_id,
        'start_at': start,
        'duration_minutes': duration_minutes,
        'status': 'scheduled',
        'reason': reason
    }
    appointments.append(new_appointment)
    return new_appointment


@router.get('/appointments')
async def get_appointments(doctor_id: int = None, patient_id: int = None,
                           status: str = None, date: str = None):
    day = None
    if date is not None:
        try:
            day = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(422, 'Дату нужно писать так: 2026-12-01')
    result = []
    for item in appointments:
        if doctor_id is not None and item['doctor_id'] != doctor_id:
            continue
        if patient_id is not None and item['patient_id'] != patient_id:
            continue
        if status is not None and item['status'] != status:
            continue
        if day is not None and item['start_at'].date() != day.date():
            continue
        result.append(item)
    return result


@router.get('/appointments/{appointment_id}')
async def get_appointment(appointment_id: int):
    for item in appointments:
        if item['id'] == appointment_id:
            return item
    raise HTTPException(404, 'Запись не найдена!')


@router.patch('/appointments/{appointment_id}')
async def update_appointment(appointment_id: int, doctor_id: int = None, start_at: str = None,
                             duration_minutes: int = None, reason: str = None):
    for item in appointments:
        if item['id'] == appointment_id:
            if item['status'] != 'scheduled':
                raise HTTPException(409, 'Изменять можно только запись со статусом scheduled!')

            new_doctor_id = item['doctor_id']
            new_start = item['start_at']
            new_duration = item['duration_minutes']

            if doctor_id is not None:
                found_doctor = None
                for doctor in doctors:
                    if doctor['id'] == doctor_id:
                        found_doctor = doctor
                if found_doctor is None:
                    raise HTTPException(404, 'Врач не найден!')
                if found_doctor['is_active'] == False:
                    raise HTTPException(409, 'Врач сейчас не принимает записи!')
                new_doctor_id = doctor_id

            if start_at is not None:
                try:
                    new_start = datetime.strptime(start_at, '%Y-%m-%d %H:%M')
                except ValueError:
                    raise HTTPException(422, 'Время нужно писать так: 2026-12-01 10:00')
                if new_start <= datetime.now():
                    raise HTTPException(422, 'Время приёма должно быть в будущем!')

            if duration_minutes is not None:
                if duration_minutes not in [15, 30, 45, 60]:
                    raise HTTPException(422, 'Длительность должна быть 15, 30, 45 или 60 минут!')
                new_duration = duration_minutes

            new_end = new_start + timedelta(minutes=new_duration)
            for other in appointments:
                if other['id'] != appointment_id and other['doctor_id'] == new_doctor_id and other['status'] == 'scheduled':
                    other_end = other['start_at'] + timedelta(minutes=other['duration_minutes'])
                    if new_start < other_end and other['start_at'] < new_end:
                        raise HTTPException(409, 'У врача уже есть запись на это время!')

            item['doctor_id'] = new_doctor_id
            item['start_at'] = new_start
            item['duration_minutes'] = new_duration
            if reason is not None:
                item['reason'] = reason
            return item
    raise HTTPException(404, 'Запись не найдена!')


@router.patch('/appointments/{appointment_id}/cancel')
async def cancel_appointment(appointment_id: int):
    for item in appointments:
        if item['id'] == appointment_id:
            if item['status'] == 'cancelled':
                raise HTTPException(409, 'Запись уже отменена!')
            if item['status'] == 'completed':
                raise HTTPException(409, 'Завершённую запись отменить нельзя!')
            item['status'] = 'cancelled'
            return item
    raise HTTPException(404, 'Запись не найдена!')


@router.patch('/appointments/{appointment_id}/complete')
async def complete_appointment(appointment_id: int):
    for item in appointments:
        if item['id'] == appointment_id:
            if item['status'] == 'cancelled':
                raise HTTPException(409, 'Отменённую запись завершить нельзя!')
            if item['status'] == 'completed':
                raise HTTPException(409, 'Запись уже завершена!')
            item_end = item['start_at'] + timedelta(minutes=item['duration_minutes'])
            if datetime.now() < item_end:
                raise HTTPException(409, 'Приём ещё не закончился!')
            item['status'] = 'completed'
            return item
    raise HTTPException(404, 'Запись не найдена!')


@router.get('/doctors/{doctor_id}/appointments')
async def get_doctor_appointments(doctor_id: int):
    for doctor in doctors:
        if doctor['id'] == doctor_id:
            result = []
            for item in appointments:
                if item['doctor_id'] == doctor_id:
                    result.append(item)
            return result
    raise HTTPException(404, 'Врач не найден!')


@router.get('/patients/{patient_id}/appointments')
async def get_patient_appointments(patient_id: int):
    for patient in patients:
        if patient['id'] == patient_id:
            result = []
            for item in appointments:
                if item['patient_id'] == patient_id:
                    result.append(item)
            return result
    raise HTTPException(404, 'Пациент не найден!')


app.include_router(router)