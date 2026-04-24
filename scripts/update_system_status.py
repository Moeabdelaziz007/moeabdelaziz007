import re
import random
import datetime

# Simulated Live Data Generation
def generate_metrics():
    # In a real scenario, this could hit an API or read actual server logs
    now = datetime.datetime.now(datetime.timezone.utc)
    date_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")

    visitors = random.randint(1500, 5000)
    active_agents = random.randint(40, 120)
    uptime_days = random.randint(100, 300)

    html = f"""
<div align="center">
  <table>
    <tr>
      <td align="center"><b>🟢 System Status</b><br>Active</td>
      <td align="center"><b>👥 Live Traffic</b><br>{visitors} Sessions</td>
      <td align="center"><b>🤖 Active Agents</b><br>{active_agents} Threads</td>
      <td align="center"><b>⏱️ Uptime</b><br>{uptime_days} Days</td>
    </tr>
  </table>
  <p><i>Last Updated: {date_str}</i></p>
</div>
"""
    return html

def main():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            readme_content = f.read()

        metrics_html = generate_metrics()

        # Define the tags
        start_tag = '<!-- START_LIVE_DATA -->'
        end_tag = '<!-- END_LIVE_DATA -->'

        # Replace the content between the tags
        pattern = re.compile(rf'{start_tag}.*?{end_tag}', re.DOTALL)

        if not re.search(pattern, readme_content):
            print("Tags not found in README.md. Please ensure <!-- START_LIVE_DATA --> and <!-- END_LIVE_DATA --> exist.")
            return

        new_content = re.sub(pattern, f"{start_tag}\n{metrics_html}\n{end_tag}", readme_content)

        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("Successfully updated README.md with live metrics.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
