from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


from main import app, logger


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	errors = []
	for error in exc.errors():
		# Форматируем ошибки в более простой и понятный вид
		field = " -> ".join(str(loc) for loc in error.get("loc", []))
		message = error.get("msg")
		errors.append({"field": field, "message": message})

	return JSONResponse(
		status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
		content={
			"error": "Validation Error",
			"detail": "Переданы некорректные данные.",
			"errors": errors
		}
	)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
	logger.error(f"Database IntegrityError: {str(exc)}")
	return JSONResponse(
		status_code=status.HTTP_400_BAD_REQUEST,
		content={
			"error": "Database Error",
			"detail": "Запись с такими данными уже существует в базе данных."
		}
	)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
	logger.error(f"Database error occurred: {str(exc)}")
	return JSONResponse(
		status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
		content={
			"error": "Database Connection Error",
			"detail": "Ошибка при работе с базой данных. Пожалуйста, попробуйте позже."
		}
	)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
	logger.error(f"ValueError: {str(exc)}")
	return JSONResponse(
		status_code=status.HTTP_400_BAD_REQUEST,
		content={
			"error": "Bad Request",
			"detail": str(exc)
		}
	)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
	logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
	return JSONResponse(
		status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
		content={
			"error": "Internal Server Error",
			"detail": "Произошла непредвиденная ошибка на сервере. Специалисты уже уведомлены."
		}
	)
