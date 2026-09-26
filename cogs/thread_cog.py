


import discord
from discord.ext import commands, tasks

from debug import printLog, printLogToDc
from constants import SUGGESTIONS_ID, SUGGESTIONS_NEW_TAG_ID, SUGGESTIONS_ACC_TAG_ID, SUGGESTIONS_CANT_TAG_ID, SUGGESTIONS_REJ_TAG_ID


#stuff "made" by spooks
#moved here so main file is cleaner

class ThreadMod(commands.Cog):
    def __init__(self,bot):
        self.bot=bot


    @commands.Cog.listener()
    async def on_thread_create(self,thread: discord.Thread):
        # Only handle posts created in the target forum
        if thread.parent_id!=SUGGESTIONS_ID:
            return
        forum=thread.parent

        # Find the tag by ID
        tag=discord.utils.get(forum.available_tags, id=SUGGESTIONS_NEW_TAG_ID)

        if tag is None:
            printLog("error",f"Tag {SUGGESTIONS_NEW_TAG_ID} not found")
            return

        try:
            await thread.edit(applied_tags=[*thread.applied_tags, tag])
            printLog("info",f"Applied tag {tag.name} to {thread.name}")
        except discord.Forbidden:
            printLog("error","Bot does not have permission to edit the post.")
            printLogToDc(self.bot,"error","Bot does not have permission to edit the post.")
        except discord.HTTPException as e:
            printLog("error",f"Failed to apply tag: {e}")
            printLogToDc(self.bot,"error",f"Failed to apply tag: {e}")

    @commands.Cog.listener()
    async def on_thread_update(self,before: discord.Thread, after: discord.Thread):
        #only posts in correct forum
        if after.parent_id != SUGGESTIONS_ID:
            return

        before_tags={tag.id for tag in before.applied_tags}
        after_tags={tag.id for tag in after.applied_tags}

        acc=SUGGESTIONS_ACC_TAG_ID in after_tags
        rej=SUGGESTIONS_REJ_TAG_ID in after_tags
        cant=SUGGESTIONS_CANT_TAG_ID in after_tags

        #nothing relevant was added
        if not (acc or rej or cant):
            return

        #detect newly added important tags
        acc_added=acc and SUGGESTIONS_ACC_TAG_ID not in before_tags
        rej_added=rej and SUGGESTIONS_REJ_TAG_ID not in before_tags
        cant_added=cant and SUGGESTIONS_CANT_TAG_ID not in before_tags

        #nothing new has happened
        if not (acc_added or rej_added or cant_added):
            return

        forum=after.parent
        if forum is None:
            return

        #start with current tags
        new_tags=list(after.applied_tags)

        #always remove NEW when a trigger tag is used
        new_tags=[tag for tag in new_tags if tag.id!=SUGGESTIONS_NEW_TAG_ID]

        #remove cant do tag if accepted or rejected
        if acc or rej:
            new_tags=[tag for tag in new_tags if tag.id != SUGGESTIONS_CANT_TAG_ID]

        try:
            #tag update
            if {tag.id for tag in new_tags}!=after_tags:
                await after.edit(applied_tags=new_tags)

            #lock and archive if accepted or rejected
            if acc or rej:
                await after.edit(locked=True,archived=True)

            if acc_added:
                printLog("info", f"Suggestion accepted: {after.name}")
            elif rej_added:
                printLog("info", f"Suggestion rejected: {after.name}")
            elif cant_added:
                printLog("info", f"Suggestion marked \"can't\": {after.name}")

        except discord.Forbidden:
            printLog("error","Bot does not have permission to modify/lock the post.")
            printLogToDc(self.bot,"error","Bot does not have permission to modify/lock the post.")

        except discord.HTTPException as e:
            printLog("error", f"Discord API error: {e}")



async def setup(bot):
    await bot.add_cog(ThreadMod(bot))