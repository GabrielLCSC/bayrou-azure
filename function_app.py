import azure.functions as func
import datetime
import json
import logging
from azure.cosmos import CosmosClient
import os

app = func.FunctionApp()
# Décorateur : Function Name + Trigger + Binding de sortie vers CosmosDB

# Vérifier unicité de l'email avant création user
@app.function_name(name="postUser")
@app.route(route="postUser", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@app.cosmos_db_output(
    arg_name="outputDocument",
    connection="COSMOS_CONN_STRING",
    database_name="bayroudb",
    container_name="user",
    create_if_not_exists=True
)
@app.cosmos_db_input(
    arg_name="existingUser",
    connection="COSMOS_CONN_STRING",
    database_name="bayroudb",
    container_name="user",
    sql_query="SELECT * FROM c WHERE c.email = @email",
    parameters=[{"name": "@email", "value": "{email}"}]
)
def post_user(req: func.HttpRequest, outputDocument: func.Out[func.Document], existingUser: func.DocumentList) -> func.HttpResponse:
    logging.info("Processing POST /postUser")
    try:
        body = req.get_json()
        email = body.get("email")
        if not email:
            return func.HttpResponse(
                json.dumps({"error": "Missing required field: email"}),
                mimetype="application/json",
                status_code=400
            )
        # Si user existe déjà, le retourner
        if existingUser and len(existingUser) > 0:
            user_doc = existingUser[0].to_dict()
            return func.HttpResponse(
                json.dumps({"status": "exists", "document": user_doc}),
                mimetype="application/json",
                status_code=200
            )
        # Sinon, créer le user
        document = {
            "id": email,
            "email": email
        }
        outputDocument.set(func.Document.from_dict(document))
        return func.HttpResponse(
            json.dumps({"status": "saved", "document": document}),
            mimetype="application/json",
            status_code=201
        )
    except Exception as e:
        logging.error(f"Erreur lors de l’insertion : {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
    
# Endpoint pour voter
@app.function_name(name="vote")
@app.route(route="vote", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@app.cosmos_db_output(
    arg_name="outputDocument",
    connection="COSMOS_CONN_STRING",
    database_name="bayroudb",
    container_name="vote",
    create_if_not_exists=True
)

# Empêcher le double vote (un seul vote par email)
@app.cosmos_db_input(
    arg_name="existingVotes",
    connection="COSMOS_CONN_STRING",
    database_name="bayroudb",
    container_name="vote",
    sql_query="SELECT * FROM c WHERE c.email = @email",
    parameters=[{"name": "@email", "value": "{email}"}]
)
def vote(req: func.HttpRequest, outputDocument: func.Out[func.Document], existingVotes: func.DocumentList) -> func.HttpResponse:
    logging.info("Processing POST /vote")
    try:
        body = req.get_json()
        user_id = body.get("userId")
        choice = body.get("choice")
        email = body.get("email")
        if not user_id or not choice or not email:
            return func.HttpResponse(
                json.dumps({"error": "Missing required fields: userId, choice, email"}),
                mimetype="application/json",
                status_code=400
            )
        if choice not in ["oui", "non"]:
            return func.HttpResponse(
                json.dumps({"error": "Choice must be 'oui' or 'non'"}),
                mimetype="application/json",
                status_code=400
            )
        # Vérifier si l'utilisateur a déjà voté (par email)
        if existingVotes and len(existingVotes) > 0:
            return func.HttpResponse(
                json.dumps({"error": "Vous avez déjà voté."}),
                mimetype="application/json",
                status_code=403
            )
        vote_doc = {
            "id": f"{user_id}_{datetime.datetime.utcnow().isoformat()}",
            "userId": user_id,
            "email": email,
            "choice": choice,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        outputDocument.set(func.Document.from_dict(vote_doc))
        return func.HttpResponse(
            json.dumps({"status": "vote_saved", "vote": vote_doc}),
            mimetype="application/json",
            status_code=201
        )
    except Exception as e:
        logging.error(f"Erreur lors de l’insertion du vote : {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
    
COSMOS_CONN_STRING = os.environ["COSMOS_CONN_STRING"]
client = CosmosClient.from_connection_string(COSMOS_CONN_STRING)
db = client.get_database_client("bayroudb")
vote_container = db.get_container_client("vote")

@app.function_name(name="hasVoted")
@app.route(route="hasVoted", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def has_voted(req: func.HttpRequest) -> func.HttpResponse:
    try:
        email = req.params.get("email")
        if not email:
            return func.HttpResponse(
                json.dumps({"error": "Missing email parameter"}),
                mimetype="application/json",
                status_code=400
            )

        query = "SELECT TOP 1 * FROM c WHERE c.email = @email"
        items = list(vote_container.query_items(
            query=query,
            parameters=[{"name": "@email", "value": email}],
            enable_cross_partition_query=True
        ))

        already_voted = len(items) > 0

        return func.HttpResponse(
            json.dumps({"alreadyVoted": already_voted}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

# Endpoint pour lister les votes
@app.function_name(name="listVotes")
@app.route(route="listVotes", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
@app.cosmos_db_input(
    arg_name="votes",
    connection="COSMOS_CONN_STRING",
    database_name="bayroudb",
    container_name="vote",
    sql_query="SELECT c.email, c.choice, c.timestamp FROM c"
)
def list_votes(req: func.HttpRequest, votes: func.DocumentList) -> func.HttpResponse:
    try:
        votes_list = [v.to_dict() for v in votes]
        return func.HttpResponse(
            json.dumps({"votes": votes_list}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )