# Your Project Name

This project consists of a FastAPI backend and a React frontend using Bun.

## Prerequisites

- Python 3.11 or higher
- [Poetry](https://python-poetry.org/)
- [Bun](https://bun.sh/)

## Setup and Running the Application

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Seed the database:
   ```
   poetry run seed-db
   ```

4. Start the FastAPI server:
   ```
   poetry run fastapi run app/main.py
   ```
   The backend will be available at `http://localhost:8000`.

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies using Bun:
   ```
   bun install
   ```

3. Start the development server:
   ```
   bun run dev
   ```
   The frontend will be available at `http://localhost:5173` (or another port if 5173 is occupied).

## Development

Keep both terminal windows open to run the backend and frontend concurrently. Any changes to the backend code will trigger automatic reloading of the server. Similarly, changes to the frontend code will be immediately reflected in the browser.

## Additional Information

### API Documentation

Once the backend is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

If you encounter any issues, ensure that:
1. All dependencies are correctly installed.
2. You're using the correct versions of Python, Poetry, and Bun.
3. The database has been seeded successfully.
4. Both backend and frontend servers are running simultaneously.

For more detailed information, refer to the documentation in the respective `backend` and `frontend` directories.