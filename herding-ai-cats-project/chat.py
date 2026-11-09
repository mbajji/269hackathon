import argparse
from experiment import RECIPES,CONDITIONS,system_prompt,ask
p=argparse.ArgumentParser();p.add_argument('--recipe',choices=list(RECIPES),default='pasta');p.add_argument('--condition',choices=CONDITIONS,default='combined');p.add_argument('--model',default='gemini-2.5-flash');a=p.parse_args()
print('Gemini cooking chatbot — type quit to exit')
history=[]
while True:
    try: user=input('You: ').strip()
    except (EOFError,KeyboardInterrupt): break
    if user.lower() in ('quit','exit'):break
    if not user:continue
    context='\n'.join(f'User: {u}\nAssistant: {r}' for u,r in history)+'\nUser: '+user+'\nAssistant:'
    try: answer=ask(system_prompt(a.recipe,a.condition),context,a.model)
    except Exception as e: print('Error:',e);continue
    print('Bot:',answer,'\n');history.append((user,answer))
