# Fast API Template

## To setup
```
pipenv install
pipenv shell
```

## To Run
```
python3 main.py
```

## APIs
GET /scene
POST /question
    {
        script: string,
        target: string,
        question: string
    }
POST /answer
    {
        script: string,
        answer: string
    }

