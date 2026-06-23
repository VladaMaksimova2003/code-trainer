import {
  OAUTH_PROVIDER_IDS,
  type OAuthProviderId,
} from "@/features/auth/api/oauthProviders"

interface SocialAuthProps {
  onPick?: (providerId: OAuthProviderId) => void
  title?: string
}

const ALL_SOCIAL_PROVIDERS: ReadonlyArray<{
  id: OAuthProviderId
  glyph: string
  label: string
}> = [
  { id: "vk", glyph: "VK", label: "Войти через VK" },
  { id: "google", glyph: "G", label: "Войти через Google" },
  { id: "yandex", glyph: "Я", label: "Войти через Яндекс" },
]

export default function SocialAuth({ onPick, title = "Или войдите через" }: SocialAuthProps) {
  return (
    <div className="social-subtle">
      <div className="lbl">{title}</div>
      <div className="icons">
        {ALL_SOCIAL_PROVIDERS.map((provider) => (
          <button
            key={provider.id}
            type="button"
            className={`social-ico ${provider.id}`}
            title={provider.label}
            aria-label={provider.label}
            onClick={() => onPick?.(provider.id)}
          >
            {provider.glyph}
          </button>
        ))}
      </div>
    </div>
  )
}

export { OAUTH_PROVIDER_IDS }
