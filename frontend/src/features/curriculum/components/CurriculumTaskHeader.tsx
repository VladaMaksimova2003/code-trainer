interface CurriculumTaskHeaderProps {
  curriculum: unknown
}

/** Curriculum context banner on task solver pages. */



export default function CurriculumTaskHeader({
 curriculum 
}: CurriculumTaskHeaderProps) {

  if (!curriculum) return null



  const navigation = curriculum.navigation

  const collectionLine = navigation?.collection_title_ru

    ? `Сборник «${navigation.collection_title_ru}»`

    : curriculum.theme_name_ru

      ? `Тема «${curriculum.theme_name_ru}»`

      : null



  return (

    <div className="rounded-lg border border-purple-900/40 bg-purple-950/20 px-4 py-3 space-y-1.5">

      {collectionLine ? (

        <p className="text-sm font-medium text-purple-100">{collectionLine}</p>

      ) : null}

      {curriculum.context_line_ru ? (

        <p className="text-sm text-ink-muted">{curriculum.context_line_ru}</p>

      ) : null}

      {curriculum.action_skill_label ? (

        <p className="text-sm font-medium text-ink">{curriculum.action_skill_label}</p>

      ) : null}

      {curriculum.instruction_ru ? (

        <p className="text-sm text-ink-muted">{curriculum.instruction_ru}</p>

      ) : null}

      {navigation?.task_index && navigation?.total_tasks ? (

        <p className="text-xs text-ink-faint">

          Задача {navigation.task_index} из {navigation.total_tasks} в сборнике

        </p>

      ) : null}

    </div>

  )

}


