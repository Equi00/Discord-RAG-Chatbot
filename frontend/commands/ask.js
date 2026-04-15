const { SlashCommandBuilder } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
  .setName("ask")
  .setDescription("Ask a question to the RAG bot")
  .addStringOption(option =>
    option
    .setName("question")
    .setDescription("your question")
    .setRequired(true)
  ),

  async execute(interaction) {
    const question = interaction.options.getString("question")

    await interaction.deferReply()

    try{
        const response = "Generic message"

        const message = await interaction.editReply(`${response}`)

    } catch (error) {
        await interaction.editReply("Error al procesar la consulta")
    }
  },
}