from fastapi import APIRouter, Depends, HTTPException, status

from typing import Annotated
from apps.todo.auth import get_current_active_user, auth_router
from apps.todo.models import User
from apps.todo.db import execute_query

from apps.todo.res_models import TaskResponse
from apps.todo.req_models import TaskRequest

router = APIRouter(prefix='/todo')
router.include_router(auth_router)

@router.get('/todos')
def list_tasks(user: Annotated[User, Depends(get_current_active_user)]):
    q = """
        SELECT *
        FROM todo.tasks t
        WHERE t.email = %s
    """
    d = (user.email,)
    return execute_query(q, TaskResponse, d)

@router.post('/todos')
def add_task(task:TaskRequest, user: Annotated[User, Depends(get_current_active_user)]):
    
    q = """
        INSERT INTO todo.tasks
        (email, title, description)
        VALUES(%s, %s, %s)
        RETURNING id, title, description;
    """
    d = (user.email, task.title, task.description)
    return execute_query(q, TaskResponse, d)[0]

@router.put('/todos/{id}')
def update_task(id: int, task:TaskRequest, user: Annotated[User, Depends(get_current_active_user)]):
    q = """
        SELECT *
        FROM todo.tasks t
        WHERE t.email = %s and t.id=%s
    """
    d = (user.email, id)
    try:
        execute_query(q, TaskResponse, d)[0]
    except:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail= "Task does not exist"
            )

    uq = """
        UPDATE todo.tasks
        SET title=%s, description=%s
        WHERE id=%s and email=%s
        RETURNING id, title, description;
    """
    print(task, id, user.email)
    ud = (task.title, task.description, id, user.email)
    
    return execute_query(uq, TaskResponse, ud)[0]

@router.delete('/todos/{id}')
def delete_task(id: int, user: Annotated[User, Depends(get_current_active_user)]):
    q = """
        DELETE 
        FROM todo.tasks t
        WHERE t.email = %s and t.id=%s
        RETURNING id, title, description;
    """
    d = (user.email, id)
    try:
        return execute_query(q, TaskResponse, d)[0]
    except:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail= "Task does not exist"
            )





    
  