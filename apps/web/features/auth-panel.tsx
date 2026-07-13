"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { useState } from "react";
import { z } from "zod";

import { Card, Button, Input } from "@/components/ui";
import { api } from "@/lib/api";

const registerSchema = z.object({
  preferred_name: z.string().min(2),
  email: z.string().email(),
  password: z.string().min(10),
});

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(10),
});

export function AuthPanel() {
  const router = useRouter();
  const [registerSuccess, setRegisterSuccess] = useState<string | null>(null);
  const registerForm = useForm<z.infer<typeof registerSchema>>({
    resolver: zodResolver(registerSchema),
    defaultValues: { preferred_name: "", email: "", password: "" },
  });
  const loginForm = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });
  const registerMutation = useMutation({
    mutationFn: api.register,
  });
  const loginMutation = useMutation({
    mutationFn: api.login,
  });
  const isBusy = registerMutation.isPending || loginMutation.isPending;

  async function handleRegister(values: z.infer<typeof registerSchema>) {
    setRegisterSuccess(null);
    await registerMutation.mutateAsync(values);
    loginForm.setValue("email", values.email, { shouldDirty: true });
    loginForm.setValue("password", values.password, { shouldDirty: true });
    setRegisterSuccess("Cuenta creada. Ahora entra con las mismas credenciales.");
  }

  async function handleLogin(values: z.infer<typeof loginSchema>) {
    await loginMutation.mutateAsync(values);
    router.push("/dashboard");
    router.refresh();
    window.location.assign("/dashboard");
  }

  return (
    <Card className="grid gap-6 p-6">
      <section>
        <h2 className="mb-4 text-xl font-semibold">Registro</h2>
        <form
          className="space-y-3"
          onSubmit={registerForm.handleSubmit(handleRegister)}
          noValidate
        >
          <label className="block space-y-2">
            <span className="text-sm text-muted">Nombre preferido</span>
          <Input placeholder="Nombre preferido" disabled={isBusy} {...registerForm.register("preferred_name")} />
          </label>
          {registerForm.formState.errors.preferred_name && (
            <div className="text-sm text-amber-200">{registerForm.formState.errors.preferred_name.message}</div>
          )}
          <label className="block space-y-2">
            <span className="text-sm text-muted">Correo</span>
          <Input placeholder="Correo" type="email" disabled={isBusy} {...registerForm.register("email")} />
          </label>
          {registerForm.formState.errors.email && (
            <div className="text-sm text-amber-200">{registerForm.formState.errors.email.message}</div>
          )}
          <label className="block space-y-2">
            <span className="text-sm text-muted">Contrasena</span>
          <Input placeholder="Contrasena" type="password" disabled={isBusy} {...registerForm.register("password")} />
          </label>
          <div className="text-xs text-muted">Usa al menos 10 caracteres.</div>
          {registerForm.formState.errors.password && (
            <div className="text-sm text-amber-200">{registerForm.formState.errors.password.message}</div>
          )}
          <Button type="submit" disabled={isBusy}>
            {registerMutation.isPending ? "Creando cuenta..." : "Crear cuenta"}
          </Button>
        </form>
        {registerSuccess && <div className="mt-3 text-sm text-emerald-300">{registerSuccess}</div>}
      </section>
      <section>
        <h2 className="mb-4 text-xl font-semibold">Inicio de sesion</h2>
        <form className="space-y-3" onSubmit={loginForm.handleSubmit(handleLogin)} noValidate>
          <label className="block space-y-2">
            <span className="text-sm text-muted">Correo</span>
          <Input placeholder="Correo" type="email" disabled={isBusy} {...loginForm.register("email")} />
          </label>
          {loginForm.formState.errors.email && (
            <div className="text-sm text-amber-200">{loginForm.formState.errors.email.message}</div>
          )}
          <label className="block space-y-2">
            <span className="text-sm text-muted">Contrasena</span>
          <Input placeholder="Contrasena" type="password" disabled={isBusy} {...loginForm.register("password")} />
          </label>
          {loginForm.formState.errors.password && (
            <div className="text-sm text-amber-200">{loginForm.formState.errors.password.message}</div>
          )}
          <Button type="submit" disabled={isBusy}>
            {loginMutation.isPending ? "Entrando..." : "Entrar"}
          </Button>
        </form>
      </section>
      {(registerMutation.error || loginMutation.error) && (
        <div role="alert" className="text-sm text-rose-300">
          {(registerMutation.error as Error | null)?.message ?? (loginMutation.error as Error | null)?.message}
        </div>
      )}
    </Card>
  );
}
