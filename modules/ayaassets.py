import typing
from pathlib import Path
import hikari
import lightbulb
import os
import uuid
# import apnggif
from concurrent.futures import ThreadPoolExecutor

PathLike = typing.Union[str, os.PathLike, Path, hikari.Pathish]

# ето ну да типа ррърь
class AssetManager:

    """
    Ayarou asset manager class

    Params:
        `wf`: os.PathLike[str] | str :
            Work folder path
    """

    def __init__(self, wf: PathLike):
        if wf:
            self._wf: PathLike = wf if wf.startswith('./') else './'+wf
            self._wf: PathLike = wf if wf.endswith('/') else wf+'/'
            self.__future_remove: typing.List[PathLike] = []
        else:
            raise ValueError('there should be a work folder path')

    def _clearup(self):
        if hasattr(self, '__future_remove'):
            for f in self.__future_remove:
                os.remove(f)
            self.__future_remove.clear()

    async def _write_bytes_stream(self, path: PathLike, asset: hikari.Attachment):
        with open(path, 'wb+') as f:
            async with asset.stream(executor=ThreadPoolExecutor) as stream:
                async for chunk in stream:
                    f.write(chunk)

    async def gif2apng(self, asset: hikari.Attachment) -> PathLike:
        uuid_ = str(uuid.uuid4())
        gif = f'{self._wf}{uuid_}.gif'
        apng = f'{self._wf}{uuid_}.png'

        await self._write_bytes_stream(gif, asset)
        os.system(f'./gif2apng {gif} {apng}')

        os.remove(gif)
        self.__future_remove.append(apng)
        
        return apng

    # async def apng2gif(self, asset: hikari.Attachment):
    #     uuid_ = str(uuid.uuid4())
    #     gif = f'{self._wf}{uuid_}.gif'
    #     apng = f'{self._wf}{uuid_}.png'

    #     await self._write_bytes_stream(apng, asset)
    #     apnggif.apnggif(apng, gif)

    #     os.remove(apng)
    #     self.__future_remove.append(gif)

    #     return gif

    # поприколу
    async def add_sticker(self, ctx: lightbulb.Context, name: str,  asset: hikari.File) -> hikari.GuildSticker:
        sticker = await ctx.bot.rest.create_sticker(
            ctx.guild_id,
            name=name,
            tag=name,
            image=await asset.read()
        )
        self._clearup()

        return sticker
