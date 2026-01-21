from dotenv import load_dotenv
from prolific_client.api import projects, studies, filters
from prolific_client import ProlificConfig, ProlificHttpClient

load_dotenv()  # Load .env file

def main():
    config = ProlificConfig.from_env()
    
    workspace_id = config.default_workspace_id
    
    # Check if workspace_id is empty
    if not workspace_id:
        print("ERROR: Workspace ID is empty!")
        print("\nTo find your workspace ID:")
        print("1. Go to https://app.prolific.com")
        print("2. Click on your workspace name (top left)")
        print("3. Go to Settings → API")
        print("4. Copy your Workspace ID")
        return
    
    client = ProlificHttpClient(config)
    
    try:
        response = filters.list_filters(
            client=client,
            workspace_id=workspace_id,
        )

        print("Study created successfully!")
        print(response)        

    except Exception as e:
        print(f"Error: {e}")
        print("\nPossible issues:")
        print("1. Workspace ID is incorrect")
        print("2. API token doesn't have access to this workspace")
        print("3. API token doesn't have required permissions")

if __name__ == "__main__":
    main()