import typing
import hikari
import miru

# оберточный класс для miru.SelectOption
class SelectRoleOption(miru.SelectOption):

    def __init__(self, linked_role_id: hikari.Snowflake | int, mirror_role_ids: typing.Sequence[hikari.Snowflake], **kwargs):
        self._role_id: hikari.Snowflake = linked_role_id # роль которую добавить
        self._mirror_role_ids: typing.Sequence[hikari.Snowflake] = mirror_role_ids # роли которые убирать при добавлении (может быть пустым, если не надо убирать)
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f'SelectRoleOption(role_id={self._role_id}, mirror_role_ids={self._mirror_role_ids}, '\
               f'label={self.label}, value={self.value}'

    # метод для выдачи выбранной роли и удаления ненужных (если таковые имеются)
    async def manage_linked_role(self, interaction: miru.Interaction) -> typing.Tuple[bool, hikari.Role]:
        if self._mirror_role_ids:
            for mr_id in self._mirror_role_ids:
                if mr_id in interaction.member.role_ids:
                    await interaction.member.remove_role(mr_id)

        if self._role_id not in interaction.member.role_ids:
            await interaction.member.add_role(self._role_id)
        else:
            await interaction.member.remove_role(self._role_id)

# оберточный класс для miru.View
class SelectRolesMenu(miru.View):

    options: typing.Sequence[SelectRoleOption]

    def __init__(self):
        super().__init__(timeout=None)

    # метод для нахождения опции и вызова управления ею
    async def select_roles_menu(self, select: miru.Select, ctx: miru.Context):

        for v in ctx.interaction.values:
            for o in select.options:
                if o.value == v:
                    await o.manage_linked_role(ctx.interaction)
                    continue

        await ctx.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            f'Роли обновлены',
            flags=hikari.MessageFlag.EPHEMERAL
        )

# вспомогательная функция, которую можно использовать в случаях, когда опций слишком много
def make_options_collection(*label_values: typing.Tuple[int, str, str]) -> typing.List[SelectRoleOption]:
    role_ids: typing.List[hikari.Snowflake] = [lv[0] for lv in label_values]
    res: typing.List[SelectRoleOption] = []

    for lv in label_values:
        mirror_role_ids: typing.List[hikari.Snowflake] = [r_id for r_id in role_ids if r_id != lv[0]]
        res.append(SelectRoleOption(lv[0], mirror_role_ids, label=lv[1], value=lv[2]))

    del role_ids
    return res
