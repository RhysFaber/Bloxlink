from ..structures.Bloxlink import Bloxlink # pylint: disable=import-error, no-name-in-module
from ..exceptions import Blacklisted # pylint: disable=import-error, no-name-in-module
from resources.constants import RELEASE, SERVER_INVITE # pylint: disable=import-error, no-name-in-module, no-name-in-module
from discord.errors import NotFound, Forbidden



has_premium = Bloxlink.get_module("premium", attrs=["has_premium"])
post_stats = Bloxlink.get_module("site_services", name_override="DBL", attrs="post_stats")
check_restrictions = Bloxlink.get_module("blacklist", attrs=["check_restrictions"])
set_guild_value = Bloxlink.get_module("cache", attrs=["set_guild_value"])

NOT_PRO = "**Notice - Server Not Pro**\nPro can only be used on " \
              "servers with Pro from https://blox.link.\nFind more information with the " \
              "`/donate` command. Any trouble? Message us here: " + SERVER_INVITE

WELCOME_MESSAGE = "\n\n".join([
                    "Thanks for adding Bloxlink! <:BloxlinkHappy:506622933339340830>",
                    ":exclamation: Run `/help` to view a list of commands.",
                    ":gear: Run `/setup` for an all-in-one command to set-up your server with Bloxlink.",
                    ":gear: If you're looking to change specific settings, use the `/settings` command.",
                    ":woman_office_worker: if you're looking to link Roblox groups, use the `/bind` command.",
                    "<:BloxlinkSale:506622933184020490> Interested in supercharging your Bloxlink experience? Run the `/donate` command and help support Bloxlink development!",
                    "<:BloxlinkSearch:506622933012054028> **Learn how to set-up Bloxlink:** https://blox.link/tutorial/setup/",
                    "<:BloxlinkSearch:506622933012054028> **More Bloxlink tutorials:** https://blox.link/tutorials/",
                    f"<:BloxlinkSearch:506622933012054028> **Need support?** Join our community server: {SERVER_INVITE}"])

@Bloxlink.module
class GuildJoinEvent(Bloxlink.Module):
    def __init__(self):
        pass

    async def __setup__(self):

        @Bloxlink.event
        async def on_guild_join(guild):
            try:
                await check_restrictions("guilds", guild.id)
            except Blacklisted:
                await guild.leave()
                return

            await set_guild_value(guild, hasBot=True)

            chosen_channel = None
            sorted_channels = sorted(guild.text_channels, key=lambda c: c.position, reverse=False)

            for channel in sorted_channels:
                permissions = channel.permissions_for(guild.me)

                if permissions.send_messages and permissions.read_messages:
                    chosen_channel = channel
                    break

            if RELEASE == "PRO":
                profile = await has_premium(guild=guild)

                if "pro" not in profile.features:
                    if chosen_channel:
                        try:
                            await chosen_channel.send(NOT_PRO)
                        except (NotFound, Forbidden):
                            pass

                    try:
                        await guild.leave()
                    except NotFound:
                        pass

                    return

                await set_guild_value(guild, proBot=True)

            elif RELEASE == "MAIN":
                await post_stats()

            if chosen_channel:
                try:
                    await chosen_channel.send(WELCOME_MESSAGE)
                except (NotFound, Forbidden):
                    pass
