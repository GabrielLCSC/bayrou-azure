
# Do you miss Bayrou ?

This site allows you to express your opinion on whether or not you miss François Bayrou. 


## API Reference

#### Get info on user's vote

```http
  hasVoted: [GET] https://bayrou-functionsgab.azurewebsites.net/api/hasVoted
```

#### Get all votes

```http
  listVotes: [GET] https://bayrou-functionsgab.azurewebsites.net/api/listVotes (or http://localhost:7071/ local)
```

#### Register a user

```http
  postUser: [POST] https://bayrou-functionsgab.azurewebsites.net/api/postUser (or http://localhost:7071/ local)
```

#### Register a vote linked to a user

```http
  vote: [POST] https://bayrou-functionsgab.azurewebsites.net/api/vote (or http://localhost:7071/ local)
```

# BayrouMeter – Local Testing Guide

This guide explains how to set up and run the project locally after cloning the repository.

---

## Prerequisites
Make sure you have the following installed on your machine:

- **Python 3.10+**
- **Node.js + npm**
- **Azure Functions Core Tools** (to emulate Azure Functions locally)
- **Azure CLI** (optional, for deployment to Azure)

---

## 1. Clone the repository
```bash
git clone git@github.com:GabrielLCSC/bayrou-azure.git
cd bayrou-azure
```

---

## 2. Backend (Python + Azure Functions)

1. Navigate to the backend folder (where `requirements.txt` is located).
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate    # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the Azure Functions host locally:
   ```bash
   func start
   ```

---

## 3. Frontend (index.html file)

Use this command to launch your frontend. 
```bash
   python -m http.server 8000
   ```

And go to http://localhost:8000/index.html
---

## 4. Running the full stack

- The **backend** (Azure Functions) runs at:  
  ```
  http://localhost:7071
  ```
- The **frontend** runs at:  
  ```
  http://localhost:8000/index.html
  ```

  # Project structure

<img width="865" height="570" alt="image" src="https://github.com/user-attachments/assets/4e6c73ee-8cdd-494c-a00a-bbdb325c193e" />

# KPI's insights

<img width="1449" height="842" alt="image" src="https://github.com/user-attachments/assets/a67d31fe-cf39-433b-af57-d3dbecc4984a" />


