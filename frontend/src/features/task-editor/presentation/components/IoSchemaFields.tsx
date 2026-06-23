import { IoValueKind } from "@/features/task-editor/domain/ioValue"

import type { IoSchema } from "@/features/task-editor/domain/entities"

import { editorLabelClass, editorSelectClass } from "@/features/task-editor/presentation/components/plaqueStyles"



const FORMAT_LABELS: Record<IoValueKind, string> = {

  [IoValueKind.SCALAR]: "Одно значение",

  [IoValueKind.MULTI]: "Список",

  [IoValueKind.MATRIX]: "Матрица",

  [IoValueKind.JSON]: "JSON",

}



const KIND_ORDER = [

  IoValueKind.SCALAR,

  IoValueKind.MULTI,

  IoValueKind.MATRIX,

  IoValueKind.JSON,

] as const



type Props = {

  schema: IoSchema

  onChange: (schema: IoSchema) => void

}



export function IoSchemaFields({ schema, onChange }: Props) {

  return (

    <div className="grid gap-4 sm:grid-cols-2">

      <div className="flex flex-col gap-2">

        <label className={editorLabelClass} htmlFor="io-input-format">

          Вход

        </label>

        <select

          id="io-input-format"

          className={editorSelectClass}

          value={schema.inputFormat}

          onChange={(e) =>

            onChange({ ...schema, inputFormat: e.target.value as IoValueKind })

          }

        >

          {KIND_ORDER.map((k) => (

            <option key={k} value={k}>

              {FORMAT_LABELS[k]}

            </option>

          ))}

        </select>

      </div>



      <div className="flex flex-col gap-2">

        <label className={editorLabelClass} htmlFor="io-output-format">

          Выход

        </label>

        <select

          id="io-output-format"

          className={editorSelectClass}

          value={schema.outputFormat}

          onChange={(e) =>

            onChange({ ...schema, outputFormat: e.target.value as IoValueKind })

          }

        >

          {KIND_ORDER.map((k) => (

            <option key={k} value={k}>

              {FORMAT_LABELS[k]}

            </option>

          ))}

        </select>

      </div>

    </div>

  )

}


