


import discord
from discord.ext import commands, tasks

from debug import printLog, printLogToDc
from constants import SuggestionForum
from constants import CHANNEL_IDS


#for suggestions channel
#later for other thread channels

class ThreadMod(commands.Cog):
    def __init__(self,bot):
        self.bot=bot


    @commands.Cog.listener()
    async def on_thread_create(self,thread: discord.Thread):
        # Only handle posts created in the target forum
        if thread.parent_id!=CHANNEL_IDS.SUGGESTIONS_CHANNEL_ID:
            return
        forum=thread.parent

        # Find the tag by ID
        tag=discord.utils.get(forum.available_tags, id=SuggestionForum.SuggestionTags.NEW)

        if tag is None:
            printLog("error",f"Tag {SuggestionForum.SuggestionTags.NEW} not found")
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
        if after.parent_id != CHANNEL_IDS.SUGGESTIONS_CHANNEL_ID:
            return

        before_tags={tag.id for tag in before.applied_tags}
        after_tags={tag.id for tag in after.applied_tags}

        acc=SuggestionForum.SuggestionTags.ACC in after_tags
        rej=SuggestionForum.SuggestionTags.REJ in after_tags
        cant=SuggestionForum.SuggestionTags.CANT in after_tags
        
        rej_light=SuggestionForum.SuggestionTags.REJ_LIGHT in after_tags
        more_detail=SuggestionForum.SuggestionTags.MORE_DETAIL_PLS in after_tags

        #nothing relevant was added
        if not (acc or rej or cant):
            return

        #detect newly added important tags
        acc_added=acc and SuggestionForum.SuggestionTags.ACC not in before_tags
        rej_added=rej and SuggestionForum.SuggestionTags.REJ not in before_tags
        cant_added=cant and SuggestionForum.SuggestionTags.CANT not in before_tags
        
        rej_light_added=rej_light and SuggestionForum.SuggestionTags.REJ_LIGHT not in before_tags
        more_detail_added=more_detail and SuggestionForum.SuggestionTags.MORE_DETAIL_PLS not in before_tags

        #nothing new has happened
        if not (acc_added or rej_added or cant_added or rej_light_added or more_detail_added):
            return

        forum=after.parent
        if forum is None:
            return

        #start with current tags
        new_tags=list(after.applied_tags)

        #always remove NEW when a trigger tag is used
        new_tags=[tag for tag in new_tags if tag.id!=SuggestionForum.SuggestionTags.NEW]

        if acc or rej:
            #remove cant do tag if accepted or rejected
            new_tags=[tag for tag in new_tags if tag.id != SuggestionForum.SuggestionTags.CANT]
            #remove rejected lightly tag if accepted or rejected
            new_tags=[tag for tag in new_tags if tag.id != SuggestionForum.SuggestionTags.REJ_LIGHT]

        if acc_added:
            await after.send(SuggestionForum.ACCEPTED_MESSAGE)
        elif rej_added:
            await after.send(SuggestionForum.REJECTED_MESSAGE)
        elif cant_added:
            await after.send(SuggestionForum.CANT_DO_MESSAGE)
        elif rej_light_added:
            await after.send(SuggestionForum.LIGHT_REJ_MESSAGE)
        elif more_detail_added:
            await after.send(SuggestionForum.MORE_DETAIL_MESSAGE)

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