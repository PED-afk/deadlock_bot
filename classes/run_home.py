
import discord
from discord.ext import commands
import random


class runHome(discord.ui.View):
    def __init__(self, ctx, where:str, userChar:dict, bot:commands.bot):
        super().__init__(timeout=360)#expire in x sec
        self.where=where
        self.ctx=ctx
        self.userChar=userChar
        self.bot=bot
        
        self.nextWheres=[]
        if self.where=="before start":
            nexts=bot.map_graph["start"]["nexts"]
            self.where=nexts[random.randint(0,len(nexts)-1)]
            self.nextWheres.append(self.where)
            self.nextWheres.append(self.where)
            print(self.where)
        else:
            nexts=bot.map_graph[self.where]["nexts"].copy()
            for i in range(2):
                r=random.randint(0,len(nexts)-1)
                self.nextWheres.append(nexts[r])
                nexts.pop(r)
        
        global haveToRunMore
        haveToRunMore=True

        global extraMessage
        extraMessage={}
        global doAfterInteract
        doAfterInteract={}

        global file
        file=[]
        characters=list(bot.characters.keys())
        for i in self.nextWheres:
            if "win" in i:
                haveToRunMore=False
            elif "sinner" in i:
                if "friendly" in i:
                    if random.randint(0,5)==0:
                        enemyLevel=self.userChar["Lvl"]+random.randint(-5,5)
                        enemyHP=bot.characters["Rem"]["base_HP"]+enemyLevel*bot.characters["Rem"]["perLvl"]
                        enemyHP*=random.uniform(0.3,1.0)
                        file.append(discord.File(bot.sounds_folder / "placeholder.mp3", filename=i+".mp3"))
                        if enemyHP<=self.userChar["HP"]:
                            extraMessage[i]="You met a low health Rem. You got some extra souls."
                            doAfterInteract[i]="giveSoulMany"
                        else:
                            extraMessage[i]="You met a Rem and they managed to kill you."
                            doAfterInteract[i]="die"
                    elif random.randint(0,5)==0:
                        file.append(discord.File(bot.sounds_folder / "placeholder.mp3", filename=i+".mp3"))
                        extraMessage[i]="A little helper was on the sinner, you just pass by."
                else:
                    if random.randint(0,5)==0:
                        file.append(discord.File(bot.sounds_folder / "placeholder.mp3", filename=i+".mp3"))
                        enemy=self.userChar["main"]
                        while enemy==self.userChar["main"]:
                            enemy=characters[random.randint(0,len(characters)-1)]
                        enemyLevel=self.userChar["Lvl"]+random.randint(-5,5)
                        enemyHP=bot.characters[enemy]["base_HP"]+enemyLevel*bot.characters[enemy]["perLvl"]
                        enemyHP*=random.uniform(0.3,1.0)
                        if enemyHP<=self.userChar["HP"]:
                            extraMessage[i]="You met a low health "+enemy+". You got some extra souls."
                            doAfterInteract[i]="giveSoulMany"
                        else:
                            extraMessage[i]="You met "+enemy+" and they managed to kill you."
                            doAfterInteract[i]="die"
                    elif random.randint(0,5)==0:
                        file.append(discord.File(bot.sounds_folder / "placeholder.mp3", filename=i+".mp3"))
                        extraMessage[i]="A little helper was on the sinner, you just pass by."
            elif "enemy" in i and "flank" not in i and "base" not in i:
                if "guardian" in i:
                    damage=116*random.randint(1,4)
                    extraMessage[i]="You took "+str(damage)+" damage from the enemy guardian."
                    doAfterInteract[i]="damage "+str(damage)
                elif "walker" in i:
                    print("aaaA: "+i)
                    damage=125*random.randint(1,4)
                    extraMessage[i]="You took "+str(damage)+" damage from the enemy walker."
                    doAfterInteract[i]="damage "+str(damage)
            elif "urn" in i:
                if "enemy" in i:
                    if random.randint(0,9)==0:
                        file.append(discord.File(bot.sounds_folder / "placeholder.mp3", filename=i+".mp3"))
                        enemy=self.userChar["main"]
                        while enemy==self.userChar["main"]:
                            enemy=characters[random.randint(0,len(characters)-1)]
                        enemyLevel=self.userChar["Lvl"]+random.randint(-5,5)
                        enemyHP=bot.characters[enemy]["base_HP"]+enemyLevel*bot.characters[enemy]["perLvl"]
                        enemyHP*=random.uniform(0.3,1.0)
                        if enemyHP<=self.userChar["HP"]:
                            extraMessage[i]="You ran into a low health "+enemy+". Who was trying to take the urn. You got some extra souls."
                            doAfterInteract[i]="giveSoul"
                        else:
                            extraMessage[i]="You met "+enemy+". Who was trying to take the urn. Unfortunatelly they managed to kill you."
                            doAfterInteract[i]="die"
                else:
                    if random.randint(0,19)==0:
                        file.append(discord.File(bot.sounds_folder / "placeholder.mp3", filename=i+".mp3"))
                        enemy=self.userChar["main"]
                        while enemy==self.userChar["main"]:
                            enemy=characters[random.randint(0,len(characters)-1)]
                        enemyLevel=self.userChar["Lvl"]+random.randint(-5,5)
                        enemyHP=bot.characters[enemy]["base_HP"]+enemyLevel*bot.characters[enemy]["perLvl"]
                        enemyHP*=random.uniform(0.3,1.0)
                        if enemyHP<=self.userChar["HP"]:
                            extraMessage[i]="You ran into a low health "+enemy+". Who was trying to steal the urn. You got some extra souls."
                            doAfterInteract[i]="giveSoul"
                        else:
                            extraMessage[i]="You met "+enemy+". Who was trying to steal the urn. Unfortunatelly they managed to kill you."
                            doAfterInteract[i]="die"
            else:
                doAfterInteract[i]=None
            
            if i not in doAfterInteract:
                doAfterInteract[i]=None
            if i not in extraMessage:
                extraMessage[i]=None

        print(doAfterInteract,"\n",extraMessage,"\n____")

        global nextpos
        nextpos=None
        if self.nextWheres[0] in bot.map_graph["start"]["nexts"] and self.nextWheres[1] in bot.map_graph["start"]["nexts"]:
                self.button1.label="start"
                nextpos=self.nextWheres[0]

                self.button2.label="start"
                nextpos=self.nextWheres[1]
        else:
            self.button1.label=self.nextWheres[0]
            self.button2.label=self.nextWheres[1]

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id!=self.ctx.author.id:
            await interaction.response.send_message("You can't use these buttons.",ephemeral=True,delete_after=5)
            return False
        return True

    @discord.ui.button(label="1", style=discord.ButtonStyle.primary,row=0)
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot=self.bot
        await interaction.message.delete()
        global nextpos
        global extraMessage
        if button.label=="start":
            myExtraMessage=extraMessage[nextpos]
        else:
            myExtraMessage=extraMessage[button.label]
        global doAfterInteract
        if button.label=="start":
            myDoAfterInteract=doAfterInteract[nextpos]
        else:
            myDoAfterInteract=doAfterInteract[button.label]
        global haveToRunMore
        alive=True
        if myDoAfterInteract:
            if myDoAfterInteract=="giveSoul":
                bot.user_data[str(self.ctx.author.id)]["money"]["unsecured"]+=random.randint(3,6)*100
            elif myDoAfterInteract=="giveSoulMany":
                bot.user_data[str(self.ctx.author.id)]["money"]["unsecured"]+=random.randint(3,12)*100
            elif myDoAfterInteract=="die":
                moneyLost=bot.user_data[str(self.ctx.author.id)]["money"]["unsecured"]
                bot.user_data[str(self.ctx.author.id)]["money"]["unsecured"]=0
                await interaction.response.send_message(myExtraMessage+"\nYou lost "+moneyLost+" unsecured souls")
                haveToRunMore=False
                alive=False
            elif "damage" in myDoAfterInteract:
                self.userChar["HP"]-=int(myDoAfterInteract.split(" ")[-1])
                if self.userChar["HP"]<=0:
                    haveToRunMore=False
                    alive=False
                    moneyLost=bot.user_data[str(self.ctx.author.id)]["money"]["unsecured"]
                    bot.user_data[str(self.ctx.author.id)]["money"]["unsecured"]=0
                    await interaction.response.send_message(myExtraMessage+"\nYou died to the tower and lost "+moneyLost+" unsecured souls")

        if haveToRunMore:
            if "start" in button.label:
                playerPos=nextpos
            else:
                playerPos=button.label
            if myExtraMessage==None:
                message="Your position: "+playerPos+"\n:heart:: "+str(self.userChar["HP"])+"/"+str(self.userChar["maxHP"])
            else:
                message=myExtraMessage+"\nYour position: "+playerPos+"\n:heart:: "+str(self.userChar["HP"])+"/"+str(self.userChar["maxHP"])
            global file
            if len(file)!=0:
                await interaction.response.send_message(message,view=runHome(self.ctx,self.nextWheres[0],self.userChar),files=file)
            else:
                await interaction.response.send_message(message,view=runHome(self.ctx,self.nextWheres[0],self.userChar))
        elif alive:
            await interaction.response.send_message("You got back to your base, and secured your souls.")
            userID=str(self.ctx.author.id)
            bot.user_data[userID]["money"]["secured"]+=bot.user_data[userID]["money"]["unsecured"]
            bot.user_data[userID]["money"]["unsecured"]=0
            
    @discord.ui.button(label="2", style=discord.ButtonStyle.primary,row=0)
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot=self.bot
        await interaction.message.delete()
        global nextpos
        global extraMessage
        if button.label=="start":
            myExtraMessage=extraMessage[nextpos]
        else:
            myExtraMessage=extraMessage[button.label]
        global doAfterInteract
        if button.label=="start":
            myDoAfterInteract=doAfterInteract[nextpos]
        else:
            myDoAfterInteract=doAfterInteract[button.label]
        global haveToRunMore
        alive=True
        if myDoAfterInteract:
            if myDoAfterInteract=="giveSoul":
                bot.user_data[str(self.ctx.author.id)]["money"]["unsecured"]+=random.randint(3,6)*100
            elif myDoAfterInteract=="giveSoulMany":
                bot.user_data[str(self.ctx.author.id)]["money"]["unsecured"]+=random.randint(3,12)*100
            elif myDoAfterInteract=="die":
                moneyLost=bot.user_data[str(self.ctx.author.id)]["money"]["unsecured"]
                bot.user_data[str(self.ctx.author.id)]["money"]["unsecured"]=0
                await interaction.response.send_message(myExtraMessage+"\nYou lost "+moneyLost+" unsecured souls")
                haveToRunMore=False
                alive=False
            elif "damage" in myDoAfterInteract:
                self.userChar["HP"]-=int(myDoAfterInteract.split(" ")[-1])
                if self.userChar["HP"]<=0:
                    haveToRunMore=False
                    alive=False
                    moneyLost=bot.user_data[str(self.ctx.author.id)]["money"]["unsecured"]
                    bot.user_data[str(self.ctx.author.id)]["money"]["unsecured"]=0
                    await interaction.response.send_message(myExtraMessage+"\nYou died to the tower and lost "+moneyLost+" unsecured souls")

        if haveToRunMore:
            if "start" in button.label:
                playerPos=nextpos
            else:
                playerPos=button.label
            if myExtraMessage==None:
                message="Your position: "+playerPos+"\n:heart:: "+str(self.userChar["HP"])+"/"+str(self.userChar["maxHP"])
            else:
                message=myExtraMessage+"\nYour position: "+playerPos+"\n:heart:: "+str(self.userChar["HP"])+"/"+str(self.userChar["maxHP"])
            global file
            if len(file)!=0:
                await interaction.response.send_message(message,view=runHome(self.ctx,self.nextWheres[0],self.userChar),files=file)
            else:
                await interaction.response.send_message(message,view=runHome(self.ctx,self.nextWheres[0],self.userChar))
        elif alive:
            await interaction.response.send_message("You got back to your base, and secured your souls.")
            userID=str(self.ctx.author.id)
            bot.user_data[userID]["money"]["secured"]+=bot.user_data[userID]["money"]["unsecured"]
            bot.user_data[userID]["money"]["unsecured"]=0