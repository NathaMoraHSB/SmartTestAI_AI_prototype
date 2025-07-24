# Standard libraries
import requests
import json
import base64

# App configurations and constants
from infrastructure.gpt.configs.assistant_env_config import API_KEY, API_URL
from infrastructure.gpt.configs.assistant_registry import ASSISTANTS
from infrastructure.gpt.models.assistant_name import AssistantName

# Static example/test content
from infrastructure.gpt.test_data import test_data
from infrastructure.gpt.test_data.test_data import (
    test_plan, report_text, project_name, project_description,
    test_object, test_objective, testsession_name,
    introduction_object, focus_test
)

# LanceDB instance for retrieving vector context
from infrastructure.gpt.files_intake.vector_db import db

#--------------------------Developer Context Builders--------------------------------------------------------

# Builds project context for the Exploratory Testing assistant
def build_developer_context_test_desin(project_name, project_description, testsession_name, test_object,
                                      introduction_object, focus_test):
    return f"""
    Project Name: {project_name}
    Project Description: {project_description}
    Test Session Name: {testsession_name}    
    Test Object: {test_object}
    Introduction Objects: {introduction_object}
    Focus Test: {focus_test}
    """

# Returns pre-defined interview test plan (used as developer context)
def build_developer_context_interview_questions():
    developer_content = test_plan
    return developer_content

# Returns the report text to be summarized (used as developer context)
def build_developer_context_summarizing():
    developer_content = test_data.report_text
    return developer_content

# Returns raw results table text (used as developer context)
def build_developer_context_results_table():
    developer_content = report_text
    return developer_content

#--------------------------Developer Context Router--------------------------------------------------------
# Selects appropriate developer context based on assistant type
def developer_context(assistant_name):
    if assistant_name == AssistantName.EXPLORATORY_TESTING:
        developer_text= build_developer_context_test_desin(
            project_name,
            project_description,
            testsession_name,
            test_object,
            introduction_object,
            focus_test)
    elif assistant_name == AssistantName.INTERVIEW_PREPARATION:
        developer_text=  build_developer_context_interview_questions()
    elif assistant_name == AssistantName.SUMMARIZING:
        developer_text=  build_developer_context_summarizing()
    elif assistant_name == AssistantName.TEST_RESULTS:
        developer_text=  build_developer_context_results_table()
    else:
        raise ValueError(f"Unknown assistant: {assistant_name}")
    return developer_text

#--------------------------Response Formatters Functions--------------------------------------------------------
# Format response for Exploratory Testing assistant
def manage_response_exploratory_testing(response_json):
    friendly_message = response_json.get("friendly_message", "No friendly message provided.")
    test_procedure = response_json.get("test_procedure", {})
    formatted_output = f"{friendly_message}\n\nProcedure:\n{json.dumps(test_procedure, indent=2)}"
    return formatted_output

# Format response for Interview Preparation assistant
def manage_response_interview_preparation(response_json):
    friendly_message = response_json.get("friendly_message", "No friendly message provided.")
    interview_questions = response_json.get("interview_questions", [])
    additional_notes = response_json.get("additional_notes", "")

    formatted_output = f"{friendly_message}\n\nInterview Questions:\n"

    for question in interview_questions:
        formatted_output += (
            f"Q{question['question_number']}: {question['question_text']}\n"
            f"  - Category: {question['category']}\n"
            f"  - Purpose: {question['purpose']}\n\n"
        )

    formatted_output += f"Additional Notes: {additional_notes}"
    return formatted_output

# Format response for Summarizing assistant
def manage_response_summarizing(response_json):
    friendly_message = response_json.get("friendly_message", "No friendly message provided.")
    test_summary = response_json.get("test_summary", {})

    formatted_output = f"{friendly_message}\n\nSummary:\n{json.dumps(test_summary, indent=2)}"
    return formatted_output

# Format response for Test Results assistant
def manage_response_test_results(response_json):
    friendly_message = response_json.get("friendly_message", "No friendly message provided.")
    results_table = response_json.get("results_table", [])
    additional_notes = response_json.get("additional_notes", "")

    formatted_output = f"{friendly_message}\n\nResults Table:\n"

    for row in results_table:
        formatted_output += (
            f"Area: {row['area']}\n"
            f"  - Key Findings: {row['key_findings']}\n"
            f"  - Effort Issue: {row['effort_issue']}\n"
            f"  - Quality: {row['quality']}\n\n"
        )

    formatted_output += f"Additional Notes: {additional_notes}"
    return formatted_output

#--------------------------Main Function to Send Request--------------------------------------------------------
# Main function to send a prompt and receive a formatted response
def send_request(prompt: str,
                 assistant_name: AssistantName,
                 previous_response_id: str = None,
                 image_paths: list[str] = None):

    # Retrieve assistant configuration
    cfg = ASSISTANTS.get(assistant_name)
    if not cfg:
        raise ValueError(f"Unknown assistant: {assistant_name}")

    # Vector context (only for specific assistants)
    if assistant_name in [AssistantName.EXPLORATORY_TESTING, AssistantName.INTERVIEW_PREPARATION]:
        vector_context = get_vector_context(prompt)
        combined_input = f"{vector_context}\n\n{prompt}"
    else:
        combined_input = prompt

    # Prepare message list
    system_msg = {"role": "system", "content": cfg.system}
    developer_msg = {
        "role": "developer",
        "content": developer_context(assistant_name)
    }
    user_msg = build_input_items(combined_input, image_paths)

    # Build final payload
    payload_input = [system_msg, developer_msg, user_msg]

    payload = {
        "model": "gpt-4o",
        "input": payload_input,
        "text": cfg.output_format
    }

    # Add previous response ID if provided
    if previous_response_id:
        payload["previous_response_id"] = previous_response_id


    # Debug: print payload
    print("\n[logic.py] Payload before sending:")
    print(json.dumps(payload, indent=2))

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # Send POST request to assistant API
    resp = requests.post(API_URL, headers=headers, json=payload)
    print(f"Status Code: {resp.status_code}")
    print(f"Response JSON: {resp.text}")

    if resp.status_code == 200:
        result = resp.json()
        try:
            output_content = result["output"][0]["content"][0]["text"]
            response_id = result["id"]
            # print(f"New response_id: {response_id}")

            try:
                response_json = json.loads(output_content)
                if assistant_name == AssistantName.EXPLORATORY_TESTING:
                    formatted_output = manage_response_exploratory_testing(response_json)
                elif assistant_name == AssistantName.INTERVIEW_PREPARATION:
                    formatted_output = manage_response_interview_preparation(response_json)
                elif assistant_name == AssistantName.SUMMARIZING:
                    formatted_output = manage_response_summarizing(response_json)
                elif assistant_name == AssistantName.TEST_RESULTS:
                    formatted_output = manage_response_test_results(response_json)
                else:
                    formatted_output = "Unknown assistant."

                return formatted_output, response_id

            except json.JSONDecodeError:
                print("Error parsing the JSON response.")
                return "Error parsing the JSON response.", None

        except (KeyError, IndexError) as e:
            print(f"Error extracting the assistant response: {e}")
            return "Error extracting the assistant response.", None
    else:
        error_message = f"Error: {resp.status_code} - {resp.text}"
        print(error_message)
        return error_message, None

#--------------------------Vector Context Retrieval--------------------------------------------------------
# Search LanceDB for semantically relevant content to the prompt
def get_vector_context(prompt: str, num_results: int = 10) -> str:
    table = db.open_table("files")
    results = table.search(prompt).limit(num_results).to_pandas()
    if results.empty:
        return ""

    chunks = []
    for _, row in results.iterrows():
        meta = row.get("metadata", {})
        filename = meta.get("filename", "unknown")
        page = f"p. {', '.join(map(str, meta.get('page_numbers', [])))}" if meta.get("page_numbers") else ""
        title = meta.get("title", "Untitled")
        chunks.append(f"{row['text']}\n(Source: {filename} - {page} - {title})")

    return "\n\n".join(chunks)

#--------------------------Build Input Payload with Optional Images--------------------------------------------------------

# Create the input payload for OpenAI API, including text and optional images
def build_input_items(prompt: str, image_paths: list[str] = None):
    content = [{"type": "input_text", "text": prompt}]
    if image_paths:
        for img_path in image_paths:
            with open(img_path, "rb") as img_file:
                b64_img = base64.b64encode(img_file.read()).decode("utf-8")
            content.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{b64_img}"
            })

    return {
        "role": "user",
        "content": content
    }
