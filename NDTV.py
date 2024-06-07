from bs4.element import nonwhitespace_re
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

# Function to scrape crime data for a given location
def scrape_crime_data(location):
    url = "https://www.ndtv.com/page/topic-load-more/from/allnews/type/news/page/{}/query/{}-crime"

    for page in range(1, 5):
        u = url.format(page,location)
        soup = BeautifulSoup(requests.get(u).content, "html.parser")
        crime_news = soup.find_all('li', class_='src_lst-li')

    # Check if any crime news was found
        if not crime_news:
            print(f'No crime news found for {location}.')
            return []

        crime_data = []

        # Extract relevant data from the HTML elements
        for news in crime_news:
            title_element = news.find('div', class_='src_itm-ttl').find('a')
            title = title_element.text.strip()
            date_text = news.find('span', class_='src_itm-stx').text.strip()
            date_start = date_text.rfind('|') + 1
            date = date_text[date_start:].strip()
            description_element = news.find('div', class_='src_itm-txt')
            description = description_element.text.strip() if description_element else ''
            crime_data.append({'title': title, 'date': date,
                            'description': description})

        if crime_data:
            filename = f"{location}_crime_data.csv"
            save_crime_data_to_csv(crime_data, filename, location)
            print(f"Crime data has been saved to {filename}.")
        else:
            print(f"No crime news found for {location}.")

    return True


def save_crime_data_to_csv(crime_data, filename, location):
    # Manually categorized data
    crime_types = {
        'violent_crime': ['Kills', 'kills', 'Stabbed', 'stabbed', 'Beaten', 'beaten', 'Attacked', 'attacked', 'Injured', 'injured', 'Homicide', 'homicide', 'Manslaughter', 'manslaughter', 'Slits', 'slits', 'Slit', 'slit', 'Mowed', 'mowed'],
        'sexual_crime': ['Sex', 'sex', 'Sexually', 'sexually', 'Rape', 'rape', 'Molestation', 'molestation', 'Grope', 'grope' 'Groping', 'groping', 'Groped', 'groped' 'Sexual', 'sexual', 'Abuse', 'abuse', 'Raping', 'raping'],
        'assault': ['Assaulted', 'assaulted', 'Battery', 'battery', 'Violence', 'violence', 'Attack', 'attack', 'Physical', 'physical', 'Assail', 'assail'],
        'harassment': ['Harassing', 'Harassed','harassed','Harasses','harasses','harassing', 'Harassment', 'harassment', 'Bullying', 'bullying', 'Stalking', 'stalking', 'Intimidation', 'intimidation', 'Threatening', 'threatening', 'Tortured', 'tortured', 'Ragging', 'ragging', 'Torture', 'torture'],
        'murder': ['Killed', 'killed', 'Killing', 'killing', 'Stab', 'stab', 'Stabbing', 'stabbing', 'Dead', 'dead', 'Death', 'death', 'Dies', 'dies', 'Murder', 'murder', 'Homicide', 'homicide', 'Body', 'body', 'Run Over', 'run over'],
        'arson': ['Arson', 'arson', 'Fire', 'fire', 'Burn', 'burn', 'Incendiary', 'incendiary', 'Explosion', 'explosion'],
        'suicide': ['Suicide', 'suicide', 'self-harm'],
        'kidnapping': ['Kidnap', 'kidnap', 'Kidnapped', 'kidnapped', 'Kidnapping', 'kidnapping', 'Abduction', 'abduction', 'Hostage', 'hostage', 'Captivity', 'captivity', 'Missing', 'missing'],
        'drug_related': ['Drug', 'drug', 'Narcotic', 'narcotic', 'Substance', 'substance', 'Cocaine', 'cocaine', 'Heroin', 'heroin', 'Meth', 'meth', 'Cannabis', 'cannabis', 'Marijuana', 'marijuana', 'Prescription', 'prescription'],
        'cybercrime': ['Cyber', 'cyber', 'Hacking', 'hacking', 'Online', 'online', 'Phishing', 'phishing', 'Identity', 'identity', 'Malware', 'malware', 'Ransomware', 'ransomware', 'Data', 'data', 'Breach', 'breach'],
        'weapon_related': ['Gun', 'gun', 'Firearm', 'firearm', 'Weapon', 'weapon', 'Shooting', 'shooting', 'Knife', 'knife', 'Armed', 'armed', 'Shot', 'shot'],
        'domestic_violence': ['Domestic', 'domestic', 'Violence', 'violence', 'Spousal', 'spousal', 'Partner', 'partner', 'Abuse', 'abuse'],
        'vandalism': ['Vandalism', 'vandalism', 'Graffiti', 'graffiti', 'Damage', 'damage', 'Destruction', 'destruction', 'Defacement', 'defacement'],
        'hate_crime': ['Hate', 'hate', 'Racism', 'racism', 'Discrimination', 'discrimination', 'Prejudice', 'prejudice', 'Xenophobia', 'xenophobia', 'Homophobia', 'homophobia', 'Anti-Semitic', 'anti-semitic', 'Islamophobic', 'islamophobic', 'Witch', 'witch', 'Dalit', 'dalit', 'Caste', 'caste'],
        'terrorism': ['Terrorism', 'terrorism', 'Terrorist', 'terrorist', 'Explosion', 'explosion', 'Bomb', 'bomb', 'Attack', 'attack', 'Bioterrorism', 'bioterrorism', 'Cyberterrorism', 'cyberterrorism'],
        'group_violence': ['Mob', 'mob', 'Violence', 'violence', 'Riot', 'riot', 'Clash', 'clash', 'Gang', 'gang', 'Group', 'group', 'Protest', 'protest', 'Demonstration', 'demonstration', 'Uprising', 'uprising', 'Brawl', 'brawl', 'Unrest', 'unrest', 'Revolt', 'revolt', 'Confrontation', 'confrontation', 'Disorder', 'disorder', 'Disturbance', 'disturbance'],
        'robbery': ['Robbery', 'robbery', 'Theft', 'theft', 'Steal', 'steal' 'Stole', 'stole', 'Stealing', 'stealing', 'Burglary', 'burglary', 'Larceny', 'larceny', 'Shoplifting', 'shoplifting', 'Pickpocketing', 'pickpocketing', 'Robbing', 'robbing', 'Robbed', 'robbed', 'Snatchers', 'snatchers', 'Snatching', 'snatching', 'Burglar', 'burglar'],
        'fraud': ['Cheated', 'cheated', 'Fraud', 'fraud', 'Scam', 'scam', 'Extort', 'extort', 'Forgery', 'forgery', 'Counterfeit', 'counterfeit', 'Ponzi', 'ponzi', 'Identity', 'identity', 'Leak', 'leak', 'Leaked', 'leaked', 'Conman', 'conman'],
        'corruption': ['Corruption', 'corruption', 'Bribery', 'bribery', 'Embezzlement', 'embezzlement'],
        'smuggling': ['Smuggle', 'smuggle', 'Trafficking', 'trafficking', 'Smuggling', 'smuggling', 'Bootlegging', 'bootlegging', 'Contraband', 'contraband', 'Illicit', 'illicit', 'Black market', 'black market', 'Illegal trade', 'illegal trade'],
    }

    area_types = ['Dahisar', 'Borivali', 'Kandivali', 'Malad', 'Goregoan', 'Ram Mandir', 'Jogeshwari', 'Andheri', 'Vile Parle',
                  'Santacruz', 'Khar Road', 'Bandra', 'Mahim', 'Matunga Road', 'Dadar', 'Prabhadevi', 'Lower Parel', 'Mahalaxmi',
                  'Mumbai Central', 'Grant Road', 'Charni Road', 'Marine Lines', 'Churchgate', 'Thane', 'Mulund', 'Nahur',
                  'Bhandup', 'Kanjurmarg', 'Vikroli', 'Ghatkopar', 'Vidya Vihar','Kurla','Sion','Matunga','Parel', 'Currey Road',
                  'Chinchpokli', 'Byculla','Sandhurst Road','Masjid Bunder', 'Chhatrapati Shivaji Maharaj Terminus','Chembur',
                  'Mankhurd', 'Govandi','Tilak Nagar','Chuna Bhatti', 'GTB Nagar','Wadala', 'Sewri', 'Cotton Green', 'Reay Road',
                  'Dockyard Road']


    month = datetime.strptime(crime_data[0]['date'], '%A %B %d, %Y').strftime('%m')

    unique_titles = set()
    filtered_crime_data = []

    for data in crime_data:
        if data['title'] not in unique_titles:
            unique_titles.add(data['title'])
            filtered_crime_data.append(data)


    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        with open(f"{location}_uncategorized_crimes.txt", 'w', encoding='utf-8') as uncategorized_file:

            for i, data in enumerate(filtered_crime_data):
                crime_type_count = {ctype: 0 for ctype in crime_types.keys()}

                for ctype, keywords in crime_types.items():
                    if any(keyword in data['title'] or keyword in data['description'] for keyword in keywords):
                        crime_type_count[ctype] += 1

                area_type = None
                for word in area_types:
                  if word in data['description']:
                    area_type = word
                    break

                # Find the crime type with the highest count
                crime_type = max(crime_type_count, key=crime_type_count.get)

                # Check if the crime type has zero occurrences
                if crime_type_count[crime_type] == 0:
                    crime_type = 'unknown'
                    uncategorized_file.write(f"Title: {data['title']}\n")
                    uncategorized_file.write(f"Date: {data['date']}\n")
                    uncategorized_file.write(
                        f"Description: {data['description']}\n")
                    uncategorized_file.write("\n")
                else:
                    time = datetime.strptime(data['date'], '%A %B %d, %Y').strftime('%Y-%m-%d')
                    csv_writer.writerow([location, area_type, time,
                                         crime_type, data['title'], state, month])



location = input("Enter the location: ").lower()
state = input("Enter the state: ").lower()


# run only first time
filename = f"{location}_crime_data.csv"
with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['location', 'area',
                             'time', 'crimetype', 'description', 'state', 'month'])


crime_data = scrape_crime_data(location)
