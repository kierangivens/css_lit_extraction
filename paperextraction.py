import requests
import time
import pandas as pd
import sqlite3

def fetch_with_retry(url, max_retries=5):
    for attempt in range(max_retries):
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.json()
            
        if response.status_code in [429, 500]:
            print(f"Rate limited or server error. Retrying in {2 ** attempt} seconds...")
            time.sleep(2 ** attempt)
            continue
            
        if response.status_code == 400:
            print(f"\nAPI Error Details: {response.text}\n")
            
        response.raise_for_status()
    raise Exception("Max retries exceeded")

def extract_cursor_aigc_papers():
    print("Fetching full dataset using cursor pagination...")
    
    # Notice we removed the 'page' parameter from the base_query
    base_query = (
        f"{BASE_URL}?search=AI generated content social media"
        f"&filter=publication_year:>2022"
        f"&select=id,doi,title,publication_year,authorships,cited_by_count,topics,open_access,primary_location"
        f"&per_page=100"
        f"&api_key={API_KEY}"
    )

    results = []
    
    # 1. Start with the default cursor
    current_cursor = "*"
    total_fetched = 0
    
    while current_cursor:
        # 2. Append the current cursor to the URL
        url = f"{base_query}&cursor={current_cursor}"
        
        data = fetch_with_retry(url)
        works = data.get('results', [])
        
        if not works:
            print("No more results found. Ending extraction.")
            break
            
        for work in works:
            authors = work.get('authorships', [])
            first_author_name = authors[0]['author']['display_name'] if authors else "Unknown"
            first_author_id = authors[0]['author']['id'] if authors else "Unknown"
            
            topics = work.get('topics', [])
            primary_topic = topics[0]['display_name'] if topics else "None"

            location = work.get('primary_location') or {}
            source = location.get('source') or {}
            journal_name = source.get('display_name', 'Unknown')

            oa_data = work.get('open_access') or {}
            is_open_access = oa_data.get('is_oa', False)

            results.append({
                'openalex_id': work.get('id'),
                'doi': work.get('doi'),
                'title': work.get('title'),
                'year': work.get('publication_year'),
                'first_author_name': first_author_name,
                'first_author_id': first_author_id,
                'citations': work.get('cited_by_count', 0),
                'primary_topic': primary_topic,
                'is_open_access': is_open_access,
                'journal_name': journal_name
            })
            
        total_fetched += len(works)
        print(f"Fetched {total_fetched} records so far...")
        
        # 3. Update the cursor for the next loop. 
        # If next_cursor is null, this will end the while loop.
        current_cursor = data.get('meta', {}).get('next_cursor')

    print(f"\nDone! Extracted a total of {len(results)} records.")
    return results

def save_to_sqlite(data):
    if not data: return
    df = pd.DataFrame(data)
    conn = sqlite3.connect('aigc_research_full.db')
    df.to_sql('papers', conn, if_exists='replace', index=False)
    conn.close()
    print("Saved to aigc_research_full.db!")

if __name__ == "__main__":
    data = extract_cursor_aigc_papers()
    save_to_sqlite(data)