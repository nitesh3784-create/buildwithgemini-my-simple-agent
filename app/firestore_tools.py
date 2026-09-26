# Copyright 2026 Google LLC
# Firestore tools for General IT & Tech Support Agent.

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-411423280d35"


def _get_firestore_client() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID, database="(default)")


def search_knowledge_base(query: str = "", category: str = "", error_code: str = "") -> str:
    """Searches the IT Knowledge Base in Firestore for troubleshooting guides and articles.

    Args:
        query: Optional search keyword to match against article title, symptoms, or error code.
        category: Optional category filter (e.g. 'Network', 'OS & Hardware', 'Storage', 'Security & Identity').
        error_code: Optional specific error code to filter by (e.g. 'ERR_VPN_TIMEOUT', 'BSOD_0x0000007E').

    Returns:
        Formatted summary of matching knowledge base articles.
    """
    try:
        db = _get_firestore_client()
        collection_ref = db.collection("knowledge_base")

        docs = collection_ref.stream()
        results = []

        q_lower = query.lower().strip()
        cat_lower = category.lower().strip()
        err_lower = error_code.lower().strip()

        for doc in docs:
            data = doc.to_dict()
            title = data.get("title", "")
            cat = data.get("category", "")
            err = data.get("error_code", "")
            symptoms = data.get("symptoms", "")

            # Apply filters
            if cat_lower and cat_lower not in cat.lower():
                continue
            if err_lower and err_lower not in err.lower():
                continue
            if q_lower and (q_lower not in title.lower() and q_lower not in symptoms.lower() and q_lower not in err.lower()):
                continue

            results.append(data)

        if not results:
            return f"No articles found matching query='{query}', category='{category}', error_code='{error_code}'."

        formatted_articles = []
        for r in results:
            formatted_articles.append(
                f"[{r.get('id')}] {r.get('title')}\n"
                f"  Category: {r.get('category')} | Severity: {r.get('severity')} | Error Code: {r.get('error_code')}\n"
                f"  Symptoms: {r.get('symptoms')}\n"
                f"  Resolution Steps: {r.get('resolution_steps')}"
            )

        return "\n\n".join(formatted_articles)
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"


def get_knowledge_base_article(article_id: str) -> str:
    """Retrieves a specific IT Knowledge Base article from Firestore by its ID (e.g., 'KB-101').

    Args:
        article_id: The unique identifier of the article (e.g., 'KB-101', 'KB-102').

    Returns:
        Formatted details of the knowledge base article or error message if not found.
    """
    try:
        db = _get_firestore_client()
        doc_ref = db.collection("knowledge_base").document(article_id)
        doc = doc_ref.get()

        if not doc.exists:
            return f"Article with ID '{article_id}' not found in Firestore."

        r = doc.to_dict()
        return (
            f"[{r.get('id')}] {r.get('title')}\n"
            f"Category: {r.get('category')} | Severity: {r.get('severity')} | Error Code: {r.get('error_code')}\n"
            f"Symptoms: {r.get('symptoms')}\n"
            f"Resolution Steps: {r.get('resolution_steps')}"
        )
    except Exception as e:
        return f"Error fetching article '{article_id}': {str(e)}"


def add_knowledge_base_article(
    article_id: str,
    title: str,
    category: str,
    error_code: str,
    symptoms: str,
    resolution_steps: str,
    severity: str = "Medium",
) -> str:
    """Adds or updates a troubleshooting article in the Firestore IT Knowledge Base.

    Args:
        article_id: Unique article ID (e.g., 'KB-105').
        title: Short descriptive title of the issue and fix.
        category: Category (e.g., 'Network', 'Hardware', 'Software', 'Security').
        error_code: Associated error code or identifier.
        symptoms: Description of symptoms experienced by the user.
        resolution_steps: Clear step-by-step instructions to fix the issue.
        severity: Severity level ('Low', 'Medium', 'High', 'Critical').

    Returns:
        A success message confirming the document creation/update.
    """
    try:
        db = _get_firestore_client()
        doc_ref = db.collection("knowledge_base").document(article_id)

        data = {
            "id": article_id,
            "title": title,
            "category": category,
            "error_code": error_code,
            "symptoms": symptoms,
            "resolution_steps": resolution_steps,
            "severity": severity,
        }

        doc_ref.set(data)
        return f"Successfully added/updated article [{article_id}] '{title}' in Firestore knowledge_base."
    except Exception as e:
        return f"Error adding article [{article_id}]: {str(e)}"
