import asyncio
import json
import logging
logging.basicConfig(level=logging.WARNING)

from discord.ext import commands
except ImportError:
    print("(Error 1) Discord.py is not installed.")
    sys.exit(5)
    
import asyncpg

import config

bot.remove_command('help')

async def set_codecs(con):
    await con.set_type_codec('json', schema='pg_catalog',
                             encoder=lambda v: json.dumps(v),
                             decoder=lambda v: json.loads(v))


class NovaHound(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.db_pool = None
        self.ready = asyncio.Event()
        super().__init__(*args, **kwargs)

    async def logout(self):
        await self.db_pool.close()
        await super().logout()

cogs = []

desc = 'An old-school roleplaying game in Discord.'
bot = NovaHound(command_prefix=commands.when_mentioned, description=desc)
bot.db_pool = bot.loop.run_in_executor(asyncpg.create_pool(config.dsn, init=set_codecs))

for cog in cogs:
    try:
        bot.load_extension(cog)
    except Exception as e:
        print(f'Failed to load {cog} on startup.')
        print(e)


@bot.before_invoke
async def before_invoke(ctx):
    ctx.con = await bot.db_pool.acquire()


@bot.after_invoke
async def after_invoke(ctx):
    await bot.db_pool.release(ctx.con)

bot.run(config.token)
