import json
import requests

#reads in key from bing.key
def read_bing_key():
    bing_api_key = None
    
    try:
        with open('bing.key', 'r') as f:
            bing_api_key = f.readline().strip()
    except:
        try:
            with open('../bing.key') as f:
                bing_api_key = f.readline().strip()
        except:
            raise IOError('bing.key file not found')
    
    if not bing_api_key:
        raise KeyError('Bing key not found')
        
    return bing_api_key


#runs query in bing and returns a list of top 10 with name/url/snipper combo
def run_query(search_terms):
    
    bing_key = read_bing_key()
    search_url = 'https://api.bing.microsoft.com/v7.0/search'
    headers = {'Ocp-Apim-Subscription-Key': bing_key}
    params = {'q': search_terms, 'textDecorations': True, 'textFormat': 'HTML'}
    
    #getting the response based on the setups
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    
    #parse json response to readable python lists
    results = []
    for result in search_results['webPages']['value']:
        results.append({
            'title': result['name'],
            'link': result['url'],
            'summary': result['snippet']
            })
    return results



def main():
    # Alternative solution for terminal-based interaction. DM.
    search_terms = input("Enter your query terms: ")
    results = run_query(search_terms)

    for result in results:
        print(result['title'])
        print(result['link'])
        print(result['summary'])
        print('===============')

if __name__ == '__main__':
    main()